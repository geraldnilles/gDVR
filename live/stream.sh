#!/usr/bin/env bash

# Delete all previous temp files
rm out*.*

# Set channel to ESPN to start
hdhomerun_config 1316BAD1 set /tuner0/vchannel 605

# Set Config
#hdhomerun_config 1316BAD1 save 0 - | ffmpeg -i - -vf "yadif,scale=trunc(oh*2/2)*2:480" -hls_time 10 -hls_list_size 60 -hls_wrap 100 -ac 2 -c:v libx264 --c:a libfdk_aac out.m3u8
hdhomerun_config 1316BAD1 save 0 - | ffmpeg -i -  -r 30  -vf "yadif,scale=trunc(oh*2/2)*2:480,hqdn3d" -hls_time 10 -hls_list_size 60 -hls_wrap 100 -c:v libx264 -crf 25 -c:a libfdk_aac -ac 2 out.m3u8
#hdhomerun_config 1316BAD1 save 0 - | ffmpeg -i -  -r 30  -vf "yadif,scale=trunc(oh*2/2)*2:480,hqdn3d" -c:v libx264 -crf 25 -c:a libfdk_aac -ac 2 -f dash out.mpd
#hdhomerun_config 1316BAD1 save 0 - | ffmpeg -i -  -r 30  -vf "yadif,scale=trunc(oh*2/2)*2:480,hqdn3d"  -ac 2 -f smoothstreaming out

#hdhomerun_config 1316BAD1 save 0 - | ffmpeg -i -  -r 30  -vf "yadif,scale=trunc(oh*2/2)*2:480,hqdn3d"  -c:v libx264 -b:v 500k -b:a 128k -c:a libfdk_aac -ac 2 out.ts

