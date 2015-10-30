#############
 TV Controls
#############


Intro
=====

For functions external to Kodi, i will need a mechanism to contol them.  The
biggest being the TV's volume and power.  I will use the LIRC application with a
GPIO-based LED circuit to drive it.

JSON Proxy
==========

I would like to control the volume using the Kodi app's volume controls.  By
default, these volume controls send JSON RPC command to Kodi and increase the
internal mixer volume.  AFAIK, this cannot be remapped.  To get around this, i
will setup a JSON RPC proxy.

The proxy will bridge 2 separate ports.  One port will be connected to the phone
and the other port will be connected to the Kodi instance.  When a message is
recieved from the phone, it will check the command type.  Everything besides
volume commands will be passed through.  If a volume command is recieved, it
will instead send an LIRC "irsend" command to adjust the volume accordingly. 

I will probably need to write this using the asyncore python library so that it
can handle multiple concurent TCP connections. 

Program Flow
------------

Create an asyncronous server that listens to port 80.  When a connection is
established, it will create a new connection to port 81 on the local machine.
Kodi will be configured to use port 81.

An HTTP package will be recived by the proxy. If the url is not /jsonrpc, it
will pass the data directly to the input.  Data recieved from the 81 port will
always be passed back verbatim to the host. 

If th url is /jsonrpc, the data will be parsed and check if a volume or power
command was sent.  If so, it will not pass it locally and run an irsend command. 

LIRC WebUI
==========

Until my JSON proxy is up and running, i'll create a simple webUI to send basic
commands (Volume, Power, Sleep Timer?)

A single Python script (lirc_webui.py) can be transfered to the OpenElec storage
voltage as is and run.  To make the server run automatically, you can put it in
the /storage/.config/autostart.sh folder.  Make sure to add a '&' so that it
runs in the background.  I also included my autostart script.

This folder also contains the Samsung LIRC config file for my TV.  I had to find
one with volume, power, and sleep.   Place this in the .config folder overrides
the default lirc configuration.


.. vim:tw=80
