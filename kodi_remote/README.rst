#############
 Kodi Remote
#############

Intro
=====

Motivation
----------

I would like to have a Chromecast/Youtube like user interface for Kodi.  I would like anyone on the network to be able to browse the video selection on my server and "Cast" it to any Kodi instance runing in the house.  I also want to be able to queue up multiple videos for back-to-back playback.

This portion will be in charge of controlling 

Goal
----

This is a very basic Kodi Remote control service that directs Kodi to play video files.  It will also allow for queing of video files.

Basic commands will be sent to the service over a simple telnet interface. The service will translate the simplified command to Kodi's JSON-RPC protocol and maintain a connection with each instance. When playback is complete, the Kodi interface will notify this service so any addition videos can be started.

Video Serving
-------------

All of the actual data will be served using NFS.  This project will not be serving the actual video data.  It will merely be a means of controling each instance.

User Interface
--------------

Eventually, i would like some easy user interface to control this. Something simple that my wife can use.  I will likely have a WebUI.  However, i may break that into a sub project.

