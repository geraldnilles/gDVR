######
 gDVR
######

A simple set of DVR tools made for the HDHomeRun Prime.  

The tools will be written in Python using the twisted framework.  Ideally, each tool will be independant and asyncronous.  It should be easy to upgrade or swap-out each tool.  Many of these tools will run as a daemon and use Sockets to communicate with eachother.  

Module List
===========

Capture
-------

Captures the MPEG2 stream for a set period of time and gracefully stops the recording.

Launcher
--------

Starts "Capture" instances at a given date/time.  This will emulate the old-school VCR recorder.  It will hold a list of (Name,Start-Time,Channel,Duration,priority) and will launch capture instances when necesary.


Scheduler
---------

Searches the listings for shows to record.  When a match is found, it schedules it with add it to the Launcher's list of recordings.

It will hold a list of tuples decribing shows of interest.

Transcoder
----------

Converts MPEG2 streams to H264 using ffmpeg.  It will likely be an autonomous loop that waits for MPEG2 files to be finished and start transcoding when done.

UI
--

This is probably where the most modularity will happen.

At the very minimum, there will be a .conf file for the scheduler where shows of interest are stored.  The next level of UI complexity will be a CLI that help generate a scheduler conf file.

