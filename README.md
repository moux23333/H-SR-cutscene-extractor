# H-SR-cutscene-extractor
---
USM/cg extractor for HSR, made using PyCRIusm
---
**prerequisite:**
python, 
FFMPEG.EXE(Put in Repo)
Cython

**Installing**
1. clone this repo
2. download [PyCriUsm](https://github.com/BUnipendix/PyCriUsm)
3. build PyCriUSM using `python setup.py build_ext --inplace`
4. rename the build to decrypt.pyd and replace the dll in USM folder


**Usage**
(Record keys using Iridium-SR for new cutscenes)
```
install.bat
start.bat
```
Or
```
py main.py [OPTIONS]

options:
  -h, --help         show this help message and exit
  -u <USM>, --usm <USM>  file path of USM file
  -e, --explorer     pick file using File Explorer
  -o, --open         opens video file after merging
```
