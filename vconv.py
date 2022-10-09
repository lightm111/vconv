#!/usr/bin/python3
from os import path, system as s
from subprocess import check_output
from time import time, sleep
import argparse

co = lambda cmd:check_output(cmd, shell=True).decode()[:-1]

# parsing arguments
args = argparse.ArgumentParser()
args.add_argument('file', nargs='+', help="one or more files to convert")
args.add_argument("-i", "--in_opt", default="", nargs="+", dest="in_opt", help="add or override ffmpeg input options")
args.add_argument("-o", "--out_opt", default="", nargs='+', dest="out_opt", help="add or override ffmpeg output options")
args.add_argument("-d", "--out_dir", default=".out", dest="out_dir", help="set output directory")
args.add_argument("-e", "--no_english", action="store_true", dest="ne", help="remove english dub (especially in anime)")
args.add_argument("-c", "--no_commentary", action="store_true", dest="nc", help="remove commentary audio")
args.add_argument("-t", "--cool_time", nargs=1, default=60, dest="cool_time", type=int, help="cooling time in sec to avoid overheat")

stdargs = args.parse_args()

FILE = stdargs.file       # the file list

def mc(file):
    OUT_DIR = stdargs.out_dir                                   # output directory
    #OUT_DIR = path.split(FILE)[0][0]
    #if OUT_DIR == '': OUT_DIR = ".out"
    #else: OUT_DIR += "/.out"
    IN_OPT = "-hide_banner -threads 3 " + stdargs.in_opt        # input options
    OUT_OPT = "-map 0 -c copy -c:v:0 h264_qsv \
            -profile:v:0 high -level 4.2 \
            -preset slower -pix_fmt nv12 \
            -global_quality 20 -disposition:v:1 \
            attached_pic " + stdargs.out_opt                    # output options

    # dectect and skip english dub (for anime)
    if stdargs.ne:
        try:
            AEI = co(
            "ffprobe -loglevel fatal -print_format csv -i \"%s\" -show_streams|grep audio[[:alnum:][:punct:]]*[eE]ng|cut -d \",\" -f 2" %file
                )  # audio english index
            AEI = int(AEI)-1
            OUT_OPT += " -map -0:a:%i" %AEI
            print("\033[1;31mEnglish audio detected, stream #%s\033[m" %AEI)
            sleep(1)
        except:
            AEI = 0

    # detect and skip commentary audio
    if stdargs.nc:
        try:
            ACI = co(
                "ffprobe -loglevel fatal -print_format csv -i \"%s\" -show_streams|grep audio[[:alnum:][:punct:]]*[cC]ommentary|cut -d \",\" -f 2" %f
                )   # audio commentary index
            ACI = int(ACI)-1
            OUT_OPT += " -map -0:a:%i" %ACI
            print("\033[1;31mCommentary audio detected, stream #%s\033[m" %ACI)
            sleep(1)
        except:
            ACI = 0

    # Starting converting
    print("\033[1;32mConverting {0} to the directory {1} with the following options : {2}\033[m".format(file, OUT_DIR, OUT_OPT))

    START_T = time()
    s("mkdir {3} > /dev/null 2>&1; ffmpeg {0} -i '{1}' {2} '{3}/{1}'".format(IN_OPT, file, OUT_OPT, OUT_DIR))
    END_T = time()

    # Calculating time
    T_MINUTES = int((END_T-START_T)/60)
    T_SECONDS = int(END_T-START_T)%60
    MESSAGE = "{0} \nFinished in {1}mn {2}s".format(file, T_MINUTES, T_SECONDS)

    # Comparing file size
    INI_SIZE = int(co("stat -c %s \"{0}\"".format(file)))
    FIN_SIZE = int(co("stat -c %s \".out/{0}\"".format(file)))
    RATIO = round(100.0*(FIN_SIZE-INI_SIZE)/INI_SIZE, 2)
    if (RATIO>0): RATIO = "+%s" %RATIO
    print(
        "\n\033[1;32mInitial size: {0}Mb, Final size: {1}Mb ({2}%)\n".format(
            round(INI_SIZE/1024/1024, 3),
            round(FIN_SIZE/1024/1024, 3),
            RATIO
            ),
        MESSAGE, "\033[m"
        )

    # Sending notification
    try: s("notify-send vconv '%s'" %MESSAGE)
    except: print("Done")

for file in FILE:
    mc(file)
    if len(FILE)>1: sleep(stdargs.cool_time)

