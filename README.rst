##############
 Kodi Remote
##############

Goal
====

Run a server and client program written in Node.js that auto-generates playlists
of TV epsidoes.  

Server
======

The media center will run an HTTP server.  You can select which shows/episodes
you want to play and it will push it to the selected XBMC frontend. 

Client
======

Each XBMC instance will run a client instance.

To start, it will simply run a UDP multi-cast loop so that each client can be
easily discovered.  

Wishlist
========

Random Playlist
---------------

Status: *DONE*

Randomly selects 5 sequential episodes to play.  Makes a playlist, and plays it.
And shuts of the TV when done

Timer Playlist
--------------

Status: Open

Randomly pick an episode.  Keep playing episodes until the timer expires.  Then
stop the playlist and shut off the TV

Closed Loop TV Control
----------------------

Use the TV's USB port to determine if the TV is currently on or off.  When the
TV is on, the USB port is active and there will be 5V on the VBUS pin.  When the
TV is off, the USB poart is inactive and there will be 0V on VBUS.

Using a balanced resistor divider, i will have 2.5V or 0V that can be plugged
into a Rasbperry Pi GPIO.  From there, i dont have to guess if the TV is
actually on.

Freestyle Mode
--------------

Create a mode that pauses all TV control activity.  The server will no longer
try to control the TV.  THis will be useful for when we are watching live TV
instead of watching through the XBMC.  It is also very important once the closed
loop TV control is implemented. 


.. vim:tw=80
