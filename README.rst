######
 gDVR
######

A simple set of daemon tools (currently written in Python3) to schedule,
capture, and transcode television using the HDHomeRun Prime.

Motivation
==========

Right now, MythTV is the major linux PVR software.  However, the project is
pretty large and it is not easy to separate the individual components.  I would
like to make a DVR system that follows the Unix philosophy a little better.
Each function of the DVR will be separated into its own executable and will be
run as its own thread. 

To simplify things even further, all IPC will be done using the file system.
With DVRs, you generally know you are going to record something with plenty of
notice.  Even if you want to record something immediately, adding 10s of delay
is acceptable for most people.  Therefore, periodically checking the filesystem
every minute or so is acceptable.  Also, unlike most IPC and Database formats,
a DVR does not need to be scalable.  Being able to handle 10 tuners is probably
as high as anyone would realistcally go. If you are worried about burning your
SSD or harddrives, you can create a RAM disk for he heavily updated databases. 

Each executable will be scheduled using systemd.  The frequency of each run
will vary from process to process.  For example, the capture process may want
to check for new recordings every 10 to 30 seconds to make sure it doesnt miss
a new recording.  Conversely, the fetcher may only want to run once a day/week
since TV schedules dont usually change that much.  The Scheduler may want to
run every hour or so just in case a user adds a new show to the list of shows.

With this type of system, all user-interfaces will, at the core, simply edit
text files in our filesystem.

Base Components
===============

In the beginning, i would like to set up a very basic set of components to form
a DVR system.  Each component will be able to be run, tested, and upgraded
separately.  Each component can be run manually in the command line or
automatically using systemd.

Capturer
--------

There will be a capturer process for each tuner.  The details for each tuner
will be contained in the /tuners folder.  Once the capture process is launced,
it will periodically check the /capture folder for any new jobs.  If the name
of the /capture file matches the name of the /tuner file, then the job is
intended for that tuner.  This setup ensured that only 1 tuner can be scheduled
at a time.  Once the capture process determines that the job is done, it will
be responsible of removing the job fromt he capture folder.

Scheduler
---------

The scheduler process will periodically browse the local database of TV
listings and add recordings to the schedule.  The /shows folder will contain
a file for each filter.  If a filter matches one of the episodes playing today,
it will add a file to the /schedule folder. 

Queuer
------

The queuer will periodically read all of the files in /schedule and determine
if it needs to start a capture by writing a file to the /capture folder.  The
queuer will also be in charge of conflict resolution and tuner balancing.

Fetcher
-------

The fetcher will periodically scrape all of today's listing information from an
online database and plact it in the local database. The /channels folder will
contain a file for each channel.  Each will contain a schedule that specifies
start and end times for each epsidoe playing todya.  The /episode folder will
contain a file for each episode containing details about the epsiode.


Transcoder
----------

A program that does off-line transcoding to a more recent codec (like x264).
It will likely jsut be a daemon for ffmpeg.

Cleaner
-------

A program that periodically checks for old videos and deletes them from the
hard drive.  Initially, we can set limits based on Time, size, and number of
videos.  Eventually, we will want a method for marking shows as viewed. 

Implementation Plans
====================

0.1
---

+ Basic functionality.  Be able to record a recuring recording on a certain
  time and day every week
+ Simple versions of Capturer and Queuer completed

0.2
---

+ Add Transcoding using ffmpeg
+ Simple version of transcoder that simply look for newly captured files and
  converts the video stream from MPEG2 to H264 and convers the audio to AAC

0.3
---

+ Add automatic clean-up for old recordings.
+ Implement basic version of the cleaner.

0.4
---

+ Add ability to grab listings from Schedules Direct
+ implement basic versions of fetcher and scheduler

1.0
---

+ First stable release when database file-formats are more-or-less locked
+ Basic Web Server and WebUI for setting recuring recordings and adding
  "MyShows"

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

This also allows me to use other standard UNIX tools for version control,
back-up, syncronization, etc...

Program Flow Example
====================

Single Immediate Recording
--------------------------

The simplest recording option will be to start recording a show immediately.
This would be the equivalent of pressing the record button on the DVR while
watching a show.

+ Create a file with capture details.  This file contains:

	- Recording Name
	- Channel Number
	- One of the following:

		- Stoptime (in Unix Time)
		- Duration (60s, 60m, 2h, 50 seconds, 2 Hours, etc.. are all
		  acceptable)

+ Rename the file to one of the /tuner names
+ Place that file in the /capture folder
+ The capturer process for that specific tuner will see that a new /capture file
  was created and start recording.  The recording will be put in the /recordings
  folder.
+ When current time is greater than Stoptime, the recording will stop and the
  /capture file will be deleted.

Alternatively, the /capture file can be deleted at any time.  The capturer
process will see that the file is gone and stop the recording prematurely.

Finally, the /capture file can be modified.  If this happens, the capturer will
stop the recording and immediately start the new recording. 

Manually Scheduled Recording
----------------------------

Adding complexity, the next way to record a show is by scheduling it.  This is
for 1-time shows that are not on right now, or recurring shows that are on at a
regular time.  For example, record the Super Bowl this Sunday.  Another example,
Record the Tonight Show every night weeknight from 10pm to 11pm.

+ Create a file with the event details. The file contains

	- Show's Name
	- Channel Number
	- For 1 time shows
		- Start Time (Unix Time)
		- Stop Time OR Duration (see above)
	- For recurring Shows
		- Day of Week (A string with the following SMTWRFU or 0123456)
		- Start Time (6pm or 6:30pm)
		- Duration  
	- (Optional) A signed integer with the priority.  Higher numbers being
	  higher priority.  If no number is provided, 0 is used. 
+ Place the file in the /schedule folder.  The name of the file is not important
+ The queuer process will periodically scan files in the /schedule folder and
  look for shows that should be on now.
+ When a match is found, it will make sure that this show is not already
  recording and generate a /capture file if needed.  The current date/time will
  be appended to the shows name so that recurring recordings dont overwrite. If
  all tuners are filled, the queuer will also use the priority to determine if a
  recording needs to stop early.
+ The rest of the flow is detailed above.

Automatically Scheduled Recording
---------------------------------

Adding even more complexity, we can have automatically scheduled recordings.
With this, the DVR will know what shows you want to record, find them in the TV
listing database, and automatically schedule recordings.

+ Create a file with the show details.  The file contains

	- Show's Name.  Can contain a regular expression. 
	- Channel (Optional)
	- New or All (Optional - Assumes All if not specified)
	- pre time (Optional - assumes 0 minutes) Time before scheduled start
	  time to start the recording
	- post time (Optional - Assumes 0 minutes)
+ Place the file in the /shows folder.  The filename is not important.
+ The scheduler process will constantly scan the files in the /listings folder
  to determine when a show is on.
	- Scan all the files in the /listings/channels folder and generate a
	  list of shows that are on today
	- Scan all the files in the /listings/programs folder and look for shows
	  that match one of the files in the /shows folder.
	
+ When a match is found, it will read all the files in the /schedule folder and
  make sure this show is not already sheduled.  If needed, a new /schedule file
  will be generated.

Process Management
==================

Initially, i was going to minimize the amount of processes running and try to
use a library like twisted to handle the asyncronous nature of the DVR.
However, realizing that the DVR will never scale past 5 to 10 tuners, putting
so much effort towards limiting processes wasnt important.  Giving each
comonent and tuner its own process is fine.  My server can handle it, no
problem. 

All of the processes will be managed using systemd.  Some will be daemons that run constantly and systemd will automatically restart them if they crash.  Others will be run periodically and stop when they are finished. 

Testing
-------

For testing, i will use tmux sessions for each component and a bash while loop
to run each component periodically.  That way, I can view all the error messages
if a component crashes. It also allows me to test without having root access to
stop/start systemd services. 

References
==========

.. vim:tw=80:spell
