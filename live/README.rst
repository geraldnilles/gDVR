################
 Live Streaming
################

I recently started experimenting with HTTP-based video streaming protocols.  The 2 most interesting being Apple's HLS and MPEG-DASH.  

Apple's protocol is more closed, but it is supported in many existing browsers (Safari, Android's Chome, Chromecast, VLC, XBMC, etc..).  Strangely, it is not supported by the desktop version of Chrome. It is also supported well in FFMPEG which was a pleasent surprise.  

MPEG-DASH is a more open protocol that has a lot of potential, but it is not well supported.  Desktop chrome is really the only thing supporting it right now.

For now, i will use HLS since it is well supported on the most devices.

FFMPEG Setup
============

I created a script to test the HLS encoding and streaming using ffmpeg and nginx.

I created a script with the following lines

	#!/usr/bin/env bash
	# Remove existing Chunks
	rm out*
	# Start the stream 
	hdhomerun_config 1316bad1 save 2 - | ffmpeg -i - -hls_time 10 -hls_list_size 60 -hls_wrap 100 out.m3u8
 
From left to right, this starts saving the HDHomeRun stream to the pipe.  Reads the pipe into ffmpeg.  Set the chunk size to ~10 seconds per peice.  Limits the number of advertized chunks to 60.  Limits the number of saved chunks to 100 (i wanted a buffer just in case), and output the manifest files as out.m3u8.

This script was run in a folder that is visible nginx file index.  To open on a browser, simply type the address http://server.address/path/to/hls/out.m3u8 and the live video will start playing.


User Experience
===============

There will be a simple HTML page that lets you select a channel, and start streaming on that page.  it will always output to the same directory: /live/out.m3u8.  When a stream is stopped/started or a channel is changed, the out* files will be wiped out and restarted.  

We will need to implemente a delay from when the event happens and when the video player starts streaming.  It will take ~10 seconds before the user can start viewing the video.

We will also need some sort of "lock" system that prevents multiple users from fighting over the same stream.  When the page is open, it will attempt to take control.  It will then be given a randome unique identifier.  If it wants to maintainc ontrol. it will need to check-in every 60 seconds by replying with the unique identifier.  If it does not, it will relinquish control and the next person to request will be given control.  

