# vconv
Convert H265/HEVC video codec to H264

**Usage :** `python3 vconv [OPTIONS] file`

**Options:**
> file: one or more files to convert

> -i, \--in_opt: add or override ffmpeg input options

> -o, \--out_opt: add or override ffmpeg output options

> -d, \--out_dir=.out: set output directory

> -e, \--no_english: remove english dub (especially in anime)

> -c, \--no_commentary: remove commentary audio

> -t, \--cool_time=60: cooling time in sec to avoid overheat


For now, using codec h264_qsv because this is the fastest one for my computer which is only intel integrated graphic.

I use it mainly to convert anime episodes which are mostly HEVC and my phone & TV don't support this codec.

So there is a option to remove english dub because I don't like those.

