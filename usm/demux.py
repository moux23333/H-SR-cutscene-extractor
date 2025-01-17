from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from io import FileIO, BytesIO
from logging import getLogger
from os.path import basename, splitext
from pathlib import Path
from queue import SimpleQueue
from struct import Struct

from .decrypt import VideoDecrypter
from .keys import star_rail

pool = ThreadPoolExecutor()
_key_collection = {}
logger = getLogger('CriUsmDemuxer.Demuxer')
_usm_header_struct = Struct(r'>4sLxBHBxxBLL8x')


# copy from wannacri
class ChunkType(Enum):
	INFO = b"CRID"
	VIDEO = b"@SFV"
	AUDIO = b"@SFA"
	ALPHA = b"@ALP"
	SUBTITLE = b"@SBT"
	CUE = b"@CUE"

	# Rare chunk types from Youjose's PyCriCodecs
	SFSH = b"SFSH"
	AHX = b"@AHX"
	USR = b"@USR"
	PST = b"@PST"


class PayloadType(Enum):
	STREAM = 0
	HEADER = 1
	SECTION_END = 2
	METADATA = 3



@dataclass(eq=False)
class UsmHeader:
	chunk_type: ChunkType
	chunk_size: int
	data_offset: int
	padding_size: int
	chno: int
	data_type: PayloadType
	frame_time: int
	frame_rate: int

	def __post_init__(self):
		if isinstance(self.chunk_type, (bytes, bytearray)):
			self.chunk_type = ChunkType(self.chunk_type[:4])
		if isinstance(self.data_type, int):
			self.data_type = PayloadType(self.data_type & 3)

	@classmethod
	def from_file(cls, fobj):
		return cls(*_usm_header_struct.unpack(fobj.read(_usm_header_struct.size)))


class UsmDemuxer:
	def __init__(self, video_path):
		self._name = splitext(basename(video_path))[0]
		encrypted_audio, key_map = star_rail
		key = key_map.get(self._name, 0)
		self._f = UsmFile(video_path)
		self._usm_decrypter = None
		self._thread_ref_total = 1
		if key:
			key2 = key >> 32
			key1 = key & 0xffffffff
			self._usm_decrypter = VideoDecrypter(key1, key2)
			if encrypted_audio:
				self._thread_ref_total = 2

	def export(self, output_path: str, chunk_filter_config=None):
		output_path = Path(output_path)
		# 初始化线程
		logger.debug(r'Initialize the write thread')
		writer_queue = SimpleQueue()
		writing_thread = pool.submit(self._writing_loop, output_path, writer_queue)
		video_queue = writer_queue
		audio_queue = writer_queue
		if self._usm_decrypter:
			logger.debug(r'Initialize the video decryption thread')
			video_queue = SimpleQueue()
			encrypted_video_thread = pool.submit(self._decrypt_loop,self._usm_decrypter.decrypt_video , video_queue, writer_queue)
			if self._thread_ref_total == 2:
				logger.debug(r'Initialize the audio decryption thread')
				audio_queue = SimpleQueue()
				encrypted_audio_thread = pool.submit(self._decrypt_loop, self._usm_decrypter.crypt_audio, audio_queue, writer_queue)

		for header, data in self._f.iter_chucks(chunk_filter_config):
			if header.data_type != PayloadType.STREAM:
				continue
			if header.chunk_type == ChunkType.VIDEO:
				video_queue.put((header, data))
			elif header.chunk_type == ChunkType.AUDIO:
				audio_queue.put((header, data))
		# stop
		if self._usm_decrypter is None:
			writer_queue.put((None, None))
		else:
			video_queue.put((None, None))
			logger.debug('Send video end command')
			encrypted_video_thread.result()
			if self._thread_ref_total == 2:
				logger.debug('Send audio end command')
				audio_queue.put((None, None))
				encrypted_audio_thread.result()
		return writing_thread.result()

	def _decrypt_loop(self, decrypt_func, input_queue: SimpleQueue, writer_queue: SimpleQueue):
		while True:
			header, data = input_queue.get()
			if header is None:
				break
			new_data = decrypt_func(data, len(data))
			if new_data is None:
				new_data = data
			writer_queue.put((header, new_data))
			del data
		writer_queue.put((None, None))

	def _writing_loop(self, output_path: Path, queue:SimpleQueue):
		logger= getLogger('CriUsmDemuxer.writer')
		logger.debug(r'enter success')
		count = self._thread_ref_total
		audio_cache = {}
		video = None
		audios = {}
		video_output = None
		while True:
			header, data = queue.get()
			# check
			if header is None:
				count -= 1
				if count == 0:
					break
				continue
			if header.data_type != PayloadType.STREAM:
				continue

			if header.chunk_type == ChunkType.VIDEO:
				if video_output is None:
					video = output_path / (self._name + '.ivf')
					video_output = FileIO(video, 'wb')
				video_output.write(data)
			elif header.chunk_type == ChunkType.AUDIO:
				writer = audio_cache.get(header.chno, None)
				if writer is None:
					writer = BytesIO()
					audio_cache[header.chno] = writer
				writer.write(data)

		logger.debug('quit')
		if video_output:
			logger.debug('close video file')
			video_output.close()
		for inno, buffer in audio_cache.items():
			logger.debug(f'close audio file{inno}')
			audio_name = output_path / (self._name + f'_{inno}.adx')
			audios[inno] = audio_name
			with FileIO(audio_name, 'wb') as f:
				f.write(buffer.getvalue())
			buffer.close()
		return video, audios


class UsmFile(FileIO):
	def __init__(self, video_path):
		super().__init__(video_path, 'rb')

	def iter_chucks(self, enable_types=None):
		def check_type_useful(header):
			type_config = enable_types
			for i in header.chunk_type, header.data_type:
				type_config = type_config.get(i, True)
				# 没有此项
				if type_config is True:
					return False
				# 未设置具体inno filter
				if type_config is None:
					return True
			if header.chno in type_config:
				return True
			return False

		self.seek(0, 2)
		file_size = self.tell()
		self.seek(0)
		if enable_types is None:
			enable_types = {ChunkType.AUDIO: {PayloadType.STREAM: None}, ChunkType.VIDEO: {PayloadType.STREAM: None}}
		while self.tell() < file_size:
			header = UsmHeader.from_file(self)
			size = header.chunk_size - header.data_offset - header.padding_size
			self.seek(header.data_offset - 0x18, 1)
			if check_type_useful(header):
				yield header, self.read(size)
			else:
				self.seek(size, 1)
				# logger.debug(f'unused type chunk: {header.chunk_type}')
			self.seek(header.padding_size, 1)

