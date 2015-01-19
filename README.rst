######
 gDVR
######

A simple set of daemon tools (currently written in Python3) to schedule, capture, and transcode television using the HDHomeRun Prime.

Motivation
==========

Right not, MythTV is the major linux PVR software.  However, the project is pretty large and it is not easy to separate the individual components.  I would like to make a DVR system that follows the Unix philosophy a little better.



Base Components
===============

In the beginning, i would like to set up a very basic set of components to form a DVR system.  Each component will be able to be run, tested, and upgraded separately.

Additonaly, each components will be be event-driven and asyncronous.  Right now, i am using "twisted" to accomplish this.  It makes things a little more complicated, but giving everything a client-server interface makes it easy to decouple components. 

Capturer
-------

This section simply records the video stream to the disk.  For the HDHomeRun Prime, it is an MPEG2 TS stream. A channel and duration will be provided.  The program will select a tuner, change the channel, save the stream, and stop when the duration has expired.

Scheduler
---------

A program that maintains a list of recording times and tells the capturer when to start.  It will also manage prioritization of shows.

Listing Manager
----------------

A program that scans online databases and determins when a show of interest is airing. When a match is found, it will add it to the Scheduler's list.

This will also manage the list of shows the user wants to record.

Transcoder
----------

A program that does off-line transcoding to a more recent codec (like x264).  It will likely jsut be a daemon for ffmpeg.

AddOn Components
=================

The Base Components are all you "NEED" to make a functioning DVR.  but there are other features that we could add as well.

User Interfaces
---------------

ncurses frontend, Android App, XMBC (Kodi) plugin, Web Ui, etc... There are many ways we could possible interact with the base tools.  As long as we are never hardcoded to a single UI, its all good.

Commercial Skipping
-------------------

The MythTV commerical flagger is very cool.  But looking at the source, it is tightly coupled with the Myth ecosystem.  I'd like to fork it and create a standalone commercial flagger.  It's output could be fed to the transcoder so the final video is commercial free.

Live TV w/ Time Warp
--------------------

Being able to rewind Live TV, watch behind, and catch up during commercials.  It gets a little hairy, but its a great feature to have. 

Chromecast Support
------------------

Being able to sling video to a Chromecast or Rpi would be nice. 


