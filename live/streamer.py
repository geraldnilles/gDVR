#!/usr/bin/env python
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

	def watch_channel(self,chan):
		self.stop()
		self.change(chan)
		self.start()

	def wipe(self):
		# Wipe out the entire data directory
		for f in os.listdir(self.data_path):
			if f[:3] == "out":
				os.remove(self.data_path+f)

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

	def change(self,channel):
		p = subprocess.Popen(["hdhomerun_config",
					self.device_id,
					"set",
					"/tuner"+str(self.tuner_num)+"/vchannel",
					str(channel)
					])
		p.wait()


	def start(self):
		self.stop()

		self.proc_cap = subprocess.Popen(["hdhomerun_config",
					self.device_id,
					"save",
					str(self.tuner_num),
					"-"],
					stdout=subprocess.PIPE,
					stderr=subprocess.DEVNULL)
		self.proc_stm = subprocess.Popen(["ffmpeg",
					"-i", "-",
					"-r", "30",
					"-vf", "yadif,scale=trunc(oh*a/2)*2:480",
					"-hls_time","10",
					"-hls_list_size","60",
					"-hls_wrap","100",
					"-ac","2",
					self.data_path+"out.m3u8"],
					stdin=self.proc_cap.stdout,
					stdout=subprocess.DEVNULL,
					stderr=subprocess.DEVNULL)

		self.proc_stm.wait()			
	

	# Start Stream onto XBMC	
	def sling_to_xbmc(self,ip):
		# Uses the XBMC JSON-RPC API to start streaming on this device
		pass


if __name__ == "__main__":
	s = Streamer()
	
	s.watch_channel(111)

	

