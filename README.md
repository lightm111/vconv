# vconv
Convert H265/HEVC 10bits video codec to H264 8bits

###  Description

For now, using codec h264_qsv because this is the fastest one for my computer which is only intel integrated graphic.

I use it mainly to convert anime episodes which are mostly HEVC 10bits that my phone & TV don't support.

So there is a option to remove english dub because I don't like those.

### Command line options:

``` text
usage: vconv.py [-h] [-i IN_OPT [IN_OPT ...]] [-o OUT_OPT [OUT_OPT ...]] [-d OUT_DIR] [-e] [-c] [-t COOL_TIME] file [file ...]

positional arguments:
  file                  one or more files to convert

options:
  -h, --help            show this help message and exit
  -i IN_OPT [IN_OPT ...], --in_opt IN_OPT [IN_OPT ...]
                        add or override ffmpeg input options
  -o OUT_OPT [OUT_OPT ...], --out_opt OUT_OPT [OUT_OPT ...]
                        add or override ffmpeg output options
  -d OUT_DIR, --out_dir OUT_DIR
                        set output directory
  -e, --no_english      remove english dub (especially in anime)
  -c, --no_commentary   remove commentary audio
  -t COOL_TIME, --cool_time COOL_TIME
                        cooling time in sec to avoid overheat
```
