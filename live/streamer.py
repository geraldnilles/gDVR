#!/usr/bin/env python

from twisted.internet import reactor
from twisted.web.http import HTTPFactory, HTTPChannel

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

	# Clean up the chunk data directory
	def wipe(self):
		for f in os.listdir(self.data_path):
			if f[:3] == "out":
				os.remove(self.data_path+f)

	# Stop the streaming
	def stop(self):
		# Stop the recording and wait for it to finish
		if self.proc_cap != None:
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

class Handler(HTTPChannel):
	def __init__(self):
		super(Handler,self).__init__()

		self.path = None

	def allContentReceived(self):
		msg = "Unknown Path"

		cmd = self.path[1:].lower().split("/")
		print (cmd)
		if cmd[1] == "watch":
			if len(cmd) == 3:
				self.factory.streamer.watch_channel(cmd[2])
				msg = "OK"

		if cmd[1] == "stop":
			self.factory.streamer.stop()
			msg = "OK"

		if cmd[1] == "sling":
			self.factory.streamer.sling_to_xbmc(cmd[2])
			msg = "OK"
			

		out = self.generate_response(msg)

		self.sendLine(bytes(out,"utf-8"))
		self.transport.loseConnection()

	def generate_response(self,msg):
		out = "Content-Length: "+str(len(msg))+"\n\r"
		out += "Content-Type: text/plain\n\r"
		out += "\n\r"
		out += msg
		return out

	def lineReceived(self,line):	
		super(Handler,self).lineReceived(line)
		l = line.decode("utf-8")
		if len(l) <3: 
			return

		l = l.split()

		if self.path == None and l[0] == "GET":
			self.path = l[1]

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

	reactor.run()

