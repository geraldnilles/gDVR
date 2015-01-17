#############
 Capture
#############

Option 1
========

Each tuner gets its own "Capture" Instance


Option 2
========

One capture instance handles all tuners.  

I think this is the more sane solution since we are going to use the hdhomerun_config program to handle it anyway. 

There will be a class called "Tuner" and 1 will be created for each tuner.  The subprocess module will be used to start and stop instances of the hdhomerun_config program.  

Using the socket interface, you can start, stop and check on the status of each tuner.

