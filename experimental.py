import os
import subprocess
import time
import customtkinter as ctk
import win10toast

from customtkinter import filedialog
from usm import demux

fildiag = ctk.CTk()
fildiag.withdraw()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
gui = ctk.CTk()
gui.geometry("300x400")
gui.title("HSR CG Extractor")

odir = r"./output"
fngivf = ""
fngacn = ""
fngaen = ""
fngajp = ""
fngakor = ""
ofimerg = None
usmfile = ""
converted_files = []
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


def extvid(usm_path, output_dir="./output"):
    a = demux.UsmDemuxer(usm_path)
    video_name, audio_names = a.export(output_dir)
    return video_name, audio_names


def meraud(ad, v, otfi):
    cmd = ['./ffmpeg.exe', '-i', v, '-i', ad, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
           otfi]
    subprocess.call(cmd)


def convfi(ifi, ofi):
    ffmpeg_cmd = ["ffmpeg", "-i", ifi, ofi]
    subprocess.call(ffmpeg_cmd)
    time.sleep(2)

inputtt = ""
def openfile():
    global inputtt, usmfile
    inputtt = filedialog.askopenfilename(filetypes=[("USM files", "*.usm")])
    usmfile = os.path.basename(inputtt)
    usmtext.configure(text=f"Pick USM File: {usmfile}")
    gui.update()
inp2 = 0

def selectlang(c):
    global inp2
    match c:
        case "CN":
            inp2 = 0
        case "EN":
            inp2 = 1
        case "JP":
            inp2 = 2
        case "KOR":
            inp2 = 3

def checkbox_event():
    print("Checkbox event")

def run():
    global fngivf, fngacn, fngaen, fngajp, fngakor, ofimerg, inp2, inputtt
    ext = extvid(inputtt)
    for root, dirs, files in os.walk(odir):
        for file in files:
            file_path = os.path.join(root, file)
            file_name, file_ext = os.path.splitext(file)
            match file_ext:
                case ".ivf":
                    output_file = f"./output/converted/{file_name}.mp4"
                    convfi(file_path, output_file)
                    converted_files.append(file_path)
                    fngivf = f"./output/converted/{file_name}.mp4"
                case ".adx":
                    output_file = f"./output/converted/{file_name}.mp3"
                    convfi(file_path, output_file)
                    converted_files.append(file_path)
                    if "_0" in file_name:
                        fngacn = f"./output/converted/{file_name}.mp3"
                        ofimerg = f"./output/final/{file_name}-final.mp4"
                    elif "_1" in file_name:
                        fngaen = f"./output/converted/{file_name}.mp3"
                        ofimerg = f"./output/final/{file_name}-final.mp4"
                    elif "_2" in file_name:
                        fngajp = f"./output/converted/{file_name}.mp3"
                        ofimerg = f"./output/final/{file_name}-final.mp4"
                    elif "_3" in file_name:
                        fngakor = f"./output/converted/{file_name}.mp3"
                        ofimerg = f"./output/final/{file_name}-final.mp4"
    match inp2:
        case 0:
            meraud(fngacn, fngivf, ofimerg)
        case 1:
            meraud(fngaen, fngivf, ofimerg)
        case 2:
            meraud(fngajp, fngivf, ofimerg)
        case 3:
            meraud(fngakor, fngivf, ofimerg)
    win10toast.ToastNotifier().show_toast("HSR CG Extractor", "Finished", duration=5)
    for file_path in converted_files:
        os.remove(file_path)
    if check_var.get() == "on":
        os.system(f"start {ofimerg}")
    else:
        pass
    exit()

os.system("cls")
print(startstr)
usmtext = ctk.CTkLabel(gui, text="Pick USM File:")
usmtext.pack()
label = ctk.CTkLabel(gui, text="CTkLabel", fg_color="transparent")
ctk.CTkButton(gui, text="Browse", command=openfile, state="normal").pack()
ctk.CTkLabel(gui, text="Pick Language:").pack()
ctk.CTkComboBox(gui, values=["CN", "EN", "JP", "KOR"], command=selectlang).pack()
check_var = ctk.StringVar(value="on")
ctk.CTkCheckBox(gui, text="Open CG after done?", command=checkbox_event,
                           variable=check_var, onvalue="on", offvalue="off").pack()
runbtn = ctk.CTkButton(gui, text="run", command=run).pack()

gui.mainloop()

