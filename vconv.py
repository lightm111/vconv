#!/usr/bin/env python3
import subprocess as sp
from time import time, sleep
from rich import print
from rich.progress import *
from rich.prompt import Prompt, Confirm
import argparse, os, json

co = lambda cmd:sp.check_output(cmd, shell=True).decode()[:-1]

# parsing arguments
args = argparse.ArgumentParser()
args.add_argument('file', nargs='+', help="one or more files to convert")
args.add_argument("-i", "--in_opt", default="", nargs="+", dest="in_opt", help="add or override ffmpeg input options")
args.add_argument("-o", "--out_opt", default="", nargs='+', dest="out_opt", help="add or override ffmpeg output options")
args.add_argument("-d", "--out_dir", default=".out", dest="out_dir", help="set output directory")
args.add_argument("-e", "--no_english", action="store_true", dest="ne", help="remove english dub (especially in anime)")
args.add_argument("-c", "--no_commentary", action="store_true", dest="nc", help="remove commentary audio")
args.add_argument("-t", "--cool_time", default=60, dest="cool_time", type=int, help="cooling time in sec to avoid overheat")

stdargs = args.parse_args()

FILE = stdargs.file       # the file list
OUT_DIR = stdargs.out_dir                                   # output directory
IN_OPT = "-hide_banner -loglevel error -progress /dev/stdout -stats_period 1 -threads 3 " + stdargs.in_opt   # input options
OUT_OPT = "-map 0 -c copy -c:v:0 h264_qsv -profile:v:0 high -level 4.2 -preset slower \
        -pix_fmt nv12 -global_quality 20 -disposition:v:1 attached_pic " + stdargs.out_opt                   # output options
print(f"[bold]Converting to the directory {OUT_DIR} with the following options :\n[/] {OUT_OPT}")

def mc(infile):
    global OUT_DIR, IN_OPT, OUT_OPT
    filepath,filename = os.path.split(infile)
    if filepath=="": filepath="."
    outfile = f"{filepath}{os.sep}{OUT_DIR}{os.sep}{filename}"         # output file
    print(f"\n[bold cyan][blink]>[/blink]Now converting {filename}[/]")

    if "yuv420p10" not in co(f'ffprobe -loglevel fatal -print_format csv -i "{infile}" -show_streams'):
        if not Confirm.ask(r"[italic yellow]not an 10bit video, Continue anyway?[/]"): return 1

    # dectect and skip english dub (for anime)
    if stdargs.ne:
        try:
            AEI = co(
                f'ffprobe -loglevel fatal -print_format csv -i "{infile}" \
                    -show_streams|grep audio[[:alnum:][:punct:]]*[eE]ng|cut -d "," -f 2'
                )  # audio english index
            AEI = int(AEI)-1
            OUT_OPT += f" -map -0:a:{AEI}"
            print(f"[red]English audio detected, stream #{AEI}[/]")
            sleep(1)
        except: pass

    # detect and skip commentary audio
    if stdargs.nc:
        try:
            ACI = co(
                f'ffprobe -loglevel fatal -print_format csv -i "{infile}" \
                    -show_streams|grep audio[[:alnum:][:punct:]]*[cC]ommentary|cut -d "," -f 2'
                )   # audio commentary index
            ACI = int(ACI)-1
            OUT_OPT += f" -map -0:a:{ACI}"
            print(f"[red]Commentary audio detected, stream #{ACI}[/]")
            sleep(1)
        except: pass

    # Starting converting
    if os.path.isfile(outfile):
        cho = Prompt.ask("output file exist, overwrite/rename new/skip?", choices=["w", "r", "s"], default="s")
        if cho=="w": OUT_OPT += " -y"
        elif cho=="r":
            new_outfile = Prompt.ask("New name: ", default=outfile, show_default=False)
            new_outfile = f"{filepath}{os.sep}{OUT_DIR}{os.sep}{new_outfile}"
            if new_outfile==outfile: print("the same, overwriting..."); OUT_OPT += " -y"
            else: outfile = new_outfile
        else: print("[yellow]skiping[/]"); return 1
    cmd = f'ffmpeg {IN_OPT} -i "{infile}" {OUT_OPT} "{outfile}"'

    START_T = time()
    os.makedirs(f"{filepath}{os.sep}{OUT_DIR}", exist_ok=True)

    # progress bar
    #print(json.loads(co("mediainfo --Output=JSON '%s'" %infile)))
    try:
        nframe = int(json.loads(co(f'mediainfo --Output=JSON "{infile}"'))["media"]["track"][0]["FrameCount"])
    except TypeError:
        try: nframe = int(json.loads(
                    co(f'ffprobe -loglevel fatal -print_format json -show_streams "{infile}"')
                )["streams"][0]["nb_frames"]
            )
        except:
            print(":sad: Cannot set a proper progress bar")
            nframe = 10000
    with Progress(SpinnerColumn(), *Progress.get_default_columns()) as pro:
        tsk = pro.add_task("Converting", total=nframe)
        try:
            with sp.Popen(cmd, stdout=sp.PIPE, universal_newlines=True, shell=True) as p:
                for line in p.stdout:
                    if "frame=" not in line: continue
                    ind = int(line.split("\n")[0][6:])    # frame index
                    pro.update(tsk, completed=ind)
        except KeyboardInterrupt:
            print(f"canceling,next then")
            return 2

    END_T = time()

    # Calculating time
    T_MINUTES = int((END_T - START_T)/60)
    T_SECONDS = int(END_T - START_T)%60
    MESSAGE = f"{infile} \n[bold]Finished in {T_MINUTES}mn {T_SECONDS}s[/bold]"

    # Comparing file size
    INI_SIZE = os.stat(infile).st_size
    FIN_SIZE = os.stat(outfile).st_size
    RATIO = round(100.0*(FIN_SIZE-INI_SIZE)/INI_SIZE, 2)
    if (RATIO>0): RATIO = f"+{RATIO}"
    print(
        "\n[green]Initial size: {0}Mb, Final size: {1}Mb ({2}%)\n {3} [/]".format(
            round(INI_SIZE/1024/1024, 3),
            round(FIN_SIZE/1024/1024, 3),
            RATIO, MESSAGE
            )
        )

    # Sending notification
    try: os.system(f'notify-send vconv "{MESSAGE}"')
    except: print("Done")

# main loop
for (i, infile) in zip(range(len(FILE),0,-1), FILE):
    if infile[-3:]!='mkv': print(f"skiping {infile}"); continue
    rc = mc(infile)
    if i==1 or rc: continue
    try:
        with Progress(TextColumn("{task.description}"), TimeRemainingColumn()) as progress:
            task = progress.add_task("[bold green on red]Cooling time![/]", total=stdargs.cool_time)
            while not progress.finished:
                progress.update(task, advance=1)
                if not progress.finished: sleep(1)
    except KeyboardInterrupt:
        print("[bold red]can't wait, huh?[/]")
        sleep(1)

print(":smile: All done!")

