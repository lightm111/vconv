#!/usr/bin/python3
from os import system as s
from subprocess import check_output
from time import time, sleep
import sys

co = lambda cmd:check_output(cmd, shell=True).decode()[:-1]

f = sys.argv[1]
iopt = "-hide_banner -threads 3 "
oopt = "-map 0 -c copy -c:v:0 h264_qsv -profile:v:0 high -level 4.2 -preset slower -pix_fmt nv12 -global_quality 20 -disposition:v:1 attached_pic "

if (len(sys.argv) == 4): iopt = iopt + sys.argv[3]
if (len(sys.argv) >= 3): oopt = oopt + sys.argv[2]

try:
    aei = co(
        "ffprobe -loglevel fatal -print_format csv -i \"%s\" -show_streams|grep audio[[:alnum:][:punct:]]*[eE]ng|cut -d \",\" -f 2" %f
        )
    aei = int(aei)-1
    oopt = oopt + " -map -0:a:%i" %aei
    print("\033[1;31mEnglish audio detected, stream #%s\033[m" %aei)
    sleep(1)
except:
    aei = 0

try:
    aci = co(
        "ffprobe -loglevel fatal -print_format csv -i \"%s\" -show_streams|grep audio[[:alnum:][:punct:]]*[cC]ommentary|cut -d \",\" -f 2" %f
        )
    aci = int(aci)-1
    oopt = oopt + " -map -0:a:%i" %aci
    print("\033[1;31mCommentary audio detected, stream #%s\033[m" %aci)
    sleep(1)
except:
    aci = 0

print("\033[1;32mConverting {0} with the following options : {1}\033[m".format(f, oopt))

st = time()
s("mkdir .out > /dev/null 2>&1; ffmpeg {0} -i '{1}' {2} '.out/{1}'".format(iopt, f, oopt))
et = time()

ftm = int((et-st)/60)
fts = int(et-st)%60
msg = "Finished in {0}mn {1}s".format(ftm, fts)

inis = int(co("stat -c %s \"{0}\"".format(f)))
fins = int(co("stat -c %s \".out/{0}\"".format(f)))
pers = round(100.0*(fins-inis)/inis, 2)
if (pers>0): pers = "+%s" %pers
print(
    "\n\033[1;32mInitial size: {0}Mb, Final size: {1}Mb ({2}%)\n".format(
        round(inis/1024/1024, 3),
        round(fins/1024/1024, 3),
        pers
        ),
    msg, "\033[m"
    )

s("notify-send vconv '%s'" %msg)
