#!/usr/bin/env python

from twisted.internet import reactor
from twisted.web.http import HTTPFactory, HTTPChannel, Request

import os
import subprocess


class Streamer:
	def __init__(self):
		self.uuid = None
		self.device_id = "1316bad1"
		self.tuner_num = 2
		self.proc_stm = None
		self.proc_cap = None	
		self.data_path = "/mnt/raid/Live/data/"

	# Change Channels and restart the live stream
	def watch_channel(self,chan):
		self.stop()
		self.change(chan)
		self.start()
		print("Starting to Stream "+str(chan))

	# Clean up the chunk data directory
	def wipe(self):
		for f in os.listdir(self.data_path):
			if f[:3] == "out":
				os.remove(self.data_path+f)

	# Stop the streaming
	def stop(self):
		# Stop the recording and wait for it to finish
		if self.proc_cap != None:
			print ("Stopping the current Stream")
			self.proc_cap.terminate()
			self.proc_cap.wait()
		if self.proc_stm != None:
			self.proc_stm.terminate()
			self.proc_stm.wait()
		self.wipe()

		self.proc_stm = None
		self.proc_cap = None

	# Chnage the tuner number
	def change(self,channel):
		p = subprocess.Popen(["hdhomerun_config",
					self.device_id,
					"set",
					"/tuner"+str(self.tuner_num)+"/vchannel",
					str(channel)
					])
		p.wait()


	def status(self):
		if self.proc_stm == None:
			return "idle"
		if os.path.exists(self.data_path+"out.m3u8"):
			return "ready"
		else:
			return "preparing"

	# Start the streaming process
	def start(self):
		# Stop, just in case
		self.stop()
		# Start capturing the MPEG2 stream and pipe to stdout
		self.proc_cap = subprocess.Popen(["hdhomerun_config",
					self.device_id,
					"save",
					str(self.tuner_num),
					"-"],
					stdout=subprocess.PIPE,
					stderr=subprocess.DEVNULL)
		# Start the streaming/transcoding process and read the pipe from the
		# capture process
		self.proc_stm = subprocess.Popen(["ffmpeg",
					"-i", "-", # Use the stdin
					"-r", "30", # Convert down to 30 fps
					# Deinterlace and resize to 480p
					"-vf", "yadif,scale=trunc(oh*a/2)*2:480",
					# Set the HLS chunk size to ~10 seconds
					"-hls_time","10",
					# Set the manifest list to 60 chunks
					"-hls_list_size","60",
					# Only save 100 chunks at a time
					"-hls_wrap","100",
					# Down sample to 2 channels
					"-ac","2", ## TODO Mix all chanels
					# Set the output file path
					self.data_path+"out.m3u8"],
					# Use the input stream from the capture proc
					stdin=self.proc_cap.stdout,
					# Hide all STDOut and STD Error chatter
					stdout=subprocess.DEVNULL,
					stderr=subprocess.DEVNULL)
	

	# Start Stream onto XBMC	
	def sling_to_xbmc(self,ip):
		# Uses the XBMC JSON-RPC API to start streaming on this device
		pass

class RequestHandler(Request):

	def setByteHeader(self,a,b):
		self.setHeader(bytes(a,"utf-8"),bytes(b,"utf-8"))
	

	def process(self):
		self.setByteHeader("Content-Type","text/plain")
		msg = "Unknown Command"

		cmd = self.path.decode("utf-8")[1:].lower().split("/")[1:]
	
		if cmd[0] == "watch":
			if len(cmd) == 2:
				self.channel.factory.streamer.watch_channel(cmd[1])
				msg = "OK"

		if cmd[0] == "stop":
			self.channel.factory.streamer.stop()
			msg = "OK"

		if cmd[0] == "status":
			msg = self.channel.factory.streamer.status()

		if cmd[0] == "sling":
			self.channel.factory.streamer.sling_to_xbmc(cmd[1])
			msg = "OK"

	
		self.write(bytes(msg,"utf-8"))

		self.finish()


class Handler(HTTPChannel):
	requestFactory = RequestHandler



class Factory(HTTPFactory):
	protocol = Handler

	def __init__(self):
		super(Factory,self).__init__()
		self.streamer = Streamer()

if __name__ == "__main__":
	#s = Streamer()
	
	#s.watch_channel(681)
	#s.proc_stm.wait()

	f = Factory()
	
	reactor.listenTCP(9177,f)
	print ("gDVR Live Streamer Started")
	reactor.run()

