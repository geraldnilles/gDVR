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


.. vim:tw=80
