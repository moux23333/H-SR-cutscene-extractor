import os
import subprocess
import time
import random
import argparse
import tkinter as tk

from tkinter import filedialog
from usm import demux
from utils import logger

log = logger.log_init()
ap = argparse.ArgumentParser()
ap.add_argument("-u", "--usm", help="file path of USM file")
ap.add_argument("-e", "--explorer", action="store_true", help="pick files using File Explorer")
ap.add_argument("-o", "--open", action="store_true", help="opens video file after merging")
args = ap.parse_args()
root = tk.Tk()
root.withdraw()

odir = r"./output"
fngivf = None
fngacn = None
fngaen = None
fngajp = None
fngakor = None
ofimerg = None
inp = None
start_time2 = None
converted_files = []
globfn = None
startstr = """
██╗░░██╗██╗░██████╗██████╗░
██║░░██║╚═╝██╔════╝██╔══██╗
███████║░░░╚█████╗░██████╔╝
██╔══██║░░░░╚═══██╗██╔══██╗
██║░░██║██╗██████╔╝██║░░██║
╚═╝░░╚═╝╚═╝╚═════╝░╚═╝░░╚═╝

░█████╗░░██████╗░        ███████╗██╗░░██╗████████╗██████╗░░█████╗░░█████╗░████████╗░█████╗░██████╗░
██╔══██╗██╔════╝░        ██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗
██║░░╚═╝██║░░██╗░        █████╗░░░╚███╔╝░░░░██║░░░██████╔╝███████║██║░░╚═╝░░░██║░░░██║░░██║██████╔╝
██║░░██╗██║░░╚██╗        ██╔══╝░░░██╔██╗░░░░██║░░░██╔══██╗██╔══██║██║░░██╗░░░██║░░░██║░░██║██╔══██╗
╚█████╔╝╚██████╔╝        ███████╗██╔╝╚██╗░░░██║░░░██║░░██║██║░░██║╚█████╔╝░░░██║░░░╚█████╔╝██║░░██║
░╚════╝░░╚═════╝░        ╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝
                                Credits to BUnipendix for the decryptor
"""


def folconad(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".mp3") and f"{globfn}" in file_name:
            return False
        else:
            return True


def extvid(usm_path, output_dir="./output"):
    a = demux.UsmDemuxer(usm_path)
    video_name, audio_names = a.export(output_dir)
    return video_name, audio_names


def meraud(ad, v, otfi):
    cmd = ['./ffmpeg.exe', '-i', v, '-i', ad, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
           otfi]
    subprocess.call(cmd)


def convfi(ifi, ofi, iext, oext, ona):
    log.info(f"Converting {ona}.{iext} > {ona}.{oext}")
    ffmpeg_cmd = ["ffmpeg", "-i", ifi, ofi]
    subprocess.call(ffmpeg_cmd)
    log.info(f"Finished Converting {ona}.{iext} > {ona}.{oext}")
    time.sleep(2)


def run():
    global fngivf, fngacn, fngaen, fngajp, fngakor, ofimerg, inp, start_time2, globfn
    print(startstr)
    try:
        if args.usm:
            inp = str(args.usm)
        elif args.explorer:
            inp = filedialog.askopenfilename(filetypes=[("USM files", "*.usm")])
        else:
            inp = input("USM FILE: ")
    except Exception as e:
        log.info("No USM file selected")
        log.err(e)
        run()
    start_time = time.time()
    ext = extvid(inp)
    log.info("Extracting video...")
    time.sleep(random.randint(1, 3))
    log.info(ext)
    log.info("Converting ivf > mp4 and adx > mp3...")
    time.sleep(random.randint(1, 4))

    for root, dirs, files in os.walk(odir):
        for file in files:
            file_path = os.path.join(root, file)
            file_name, file_ext = os.path.splitext(file)

            if file_ext == ".ivf":
                output_file = f"./output/converted/{file_name}.mp4"
                convfi(file_path, output_file, "ivf", "mp4", file_name)
                converted_files.append(file_path)
                fngivf = f"./output/converted/{file_name}.mp4"
            elif file_ext == ".adx":
                output_file = f"./output/converted/{file_name}.mp3"
                convfi(file_path, output_file, "adx", "mp3", file_name)
                converted_files.append(file_path)
                if "_0" in file_name:
                    fngacn = f"./output/converted/{file_name}.mp3"
                    ofimerg = f"./output/final/{file_name}-final.mp4"
                    globfn = f"{file_name}-final.mp4"
                elif "_1" in file_name:
                    fngaen = f"./output/converted/{file_name}.mp3"
                    ofimerg = f"./output/final/{file_name}-final.mp4"
                    globfn = f"{file_name}-final.mp4"
                elif "_2" in file_name:
                    fngajp = f"./output/converted/{file_name}.mp3"
                    ofimerg = f"./output/final/{file_name}-final.mp4"
                    globfn = f"{file_name}-final.mp4"
                elif "_3" in file_name:
                    fngakor = f"./output/converted/{file_name}.mp3"
                    ofimerg = f"./output/final/{file_name}-final.mp4"
                    globfn = f"{file_name}-final.mp4"

    log.info("All conversions done")
    for file_path in converted_files:
        os.remove(file_path)
    log.info("All .ivf/.adx has been removed")
    end_time = time.time()
    if "Loop" in globfn and folconad("./output/converted"):
        pass
    else:
        inp2 = int(input(
            """
        AUDIO LANG:
        0 = cn
        1 = en
        2 = jp
        3 = kor
        
        Select: """))
        try:
            if inp2 == 0:
                start_time2 = time.time()
                meraud(fngacn, fngivf, ofimerg)
            elif inp2 == 1:
                start_time2 = time.time()
                meraud(fngaen, fngivf, ofimerg)
            elif inp2 == 2:
                start_time2 = time.time()
                meraud(fngajp, fngivf, ofimerg)
            elif inp2 == 3:
                start_time2 = time.time()
                meraud(fngakor, fngivf, ofimerg)
        except Exception as e:
            os.system("cls")
            log.info("Error Occurred")
            log.err(e)
            run()
        log.info("Audio files merged into the main MP4")
    end_time2 = time.time()
    elapsed_time = end_time - start_time
    elapsed_time2 = end_time2 - start_time2
    final_time = elapsed_time + elapsed_time2
    log.info(f"Finished in {round(final_time, 2)} seconds")
    print("Final file is in ./output/final")
    if args.open:
        os.system(f"start {ofimerg}")
    else:
        pass
    print("Press Any Key To Exit")


if __name__ == '__main__':
    os.system("cls")
    run()
    input()
