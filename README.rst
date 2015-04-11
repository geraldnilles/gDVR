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

A program that scans online databases and determins when a show of interest is
airing. When a match is found, it will add it to the Scheduler's list.

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

Filesystem Organization
=======================

Initially, i was going to create a single database to handle all of the data.
However, I like the idea of using the filesystem to organize my data.  We will
use plain text file in a folder structure to control the DVR.  This will make
things easy to understand when debuging.  It will also make it easy for very
small and very big files to coexist in the database.  Traditionally, the limit
of this type of database is scalablility.  However, the DVR does not need to
scale.  

All of the files will be stored in 1 directory which will be configurable.
Probably in the /home/ folder for the dvr user.

When the program is first launched, it will need to build a database from the
listing manager.  These database will be slip between the "Channels" folder and
the "Shows" folder. The "Channel" folder will have a text file for each channel
that contains that channel's schedule.  The "Shows" folder will have a text file
for each show that is playing this week. This file will contain details about
the show (title, actors, HD, etc...)

After this is populated, the scheduler process will be able to parse the
database periodically and look for matches.  The scheudle will look at files in
the "My Shows" folder.  These files are created by users (either directly or
through a program). These files will contain details about a particular show to
record.  It will have things like Title, HD/SD, Channel, New-Only.  The
scheduler will compare this files to the shows playing today that match. 

When a match is found, it will place files in the "Schedule" directory.  The
schedule directory can also be manually modified if you want to record something
on a channel at a specific time without using the TV listings.  The schedule
could also be put in a ical format and host it via a HTTP server.  Then we can
check the DVR shedule easily with our Phones or Google Calendar.

When the current time matches that of a scheduled recording, A file will be
placed in the "Catpure" folder.  The filename will be the tuner id that we
expect to be do the capturing.  The file will contain channel, title, and
duration/endtim  information.  Each tuner will have a separate Capture instance
running.  These instances will monitor the recording folder and look for a
filename that matches its tuner id. Once the recording is finished, the
capturer will clear the file and save the recording.  If you want to stop a
recording early, simply remove this file.  This file will also be used to know
when each tuner is busy. 

To keep track of the tuners available, there will also be a "Tuners" folder.
This will contain info about each tuner.  A capture process will be started for
each tuner in this folder. 

After a capture is complete, the transcoder process again will look for
captured files that need to be converted.   

Process Management
==================

Initially, i was going to minimize the amount of processes running and try to
use a library like twisted to handle the asyncronous nature of the DVR.
However, realizing that the DVR will never scale past 5 to 10 tuners, putting
so much effort towards limiting processes wasnt important.  Giving each
comonent and tuner its own process is fine.  My server can handle it, no
problem. 

All of the processes will be managed using systemd.  Some will be daemons that run constantly and systemd will automatically restart them if they crash.  Others will be run periodically and stop when they are finished. 


