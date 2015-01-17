#!/usr/bin/env python

import twisted
import subprocess


class tuner:
	def __init__(self,id,number):
		self.id = id
		self.number = number
		self.process = None
		self.reset()

	
	def reset(self):
		self.name = None
		self.stop_time = None
		self.start_time = None
		if self.process:
			self.process.kill()
		self.process = None

	def start(self,name,start_time,duration,channel):
		# TODO Check if name already exists
		
		self.name = name
		self.start_time = time.time()
		self.temp_name = self.name+".temp"
		# TODO Convert duration to seconds if a string prefix
		# so a string of "20m" ==> 20*60
		self.stop_time = self.start_time + duration

		subprocess.Popen([	"hdhomerun_config",
					self.id,
					save,
					self.number,
					mpeg_path+self.temp_name
				])

	def stop(self):
		self.process.kill()
		os.rename(mpeg_path+self.temp_name,mpeg_path+self.name)
		self.reset()

	def is_available(self):
		if name == None:
			return True
		else:
			return False

	# Check if the recording needs to stop or make sure the process
	# did not die prematurely 
	def check_up(self):
		# Check if the tuner is idle
		if name == None:
			return True
		# Check if the capture is done
		if time.time() > self.stop_time:
			self.stop()
			return True
		# Check if the capture died prematurely
		if self.process.poll():
			return True
		else:
			print ("Tuner %d quit prematurely"%self.number)
			
			

if __name__ == "__main__":

	pass





