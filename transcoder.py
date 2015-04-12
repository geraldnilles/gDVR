#!/usr/bin/env python

import common
import gdvr_config
import subprocess
import os

class Transcoder:
	def __init__(self):
		self.reset()

	def reset(self):
		self.process = None
		self.infile = None
		self.outfile = None
		self.path = gdvr_config.database_path+"/capture/"


	def start(self):
		if self.infile == None:
			return True
		# Remove the input extension and replace with mp4
		self.outfile = self.infile.rsplit(".",1)[0]+".mp4"
		
		self.process = subprocess.Popen(["ffmpeg", 
				# Specify Input File
				"-i",self.infile, 
				"-map", "0", # Transcode All Audio tracks
				# Scale to DVD Quality and apply deinterlacin
				"-vf", "yadif,scale=trunc(oh*a/2)*2:480", 
				# Use h264 codec
				"-c:v", "libx264",
				# Use high computation encoding 
				"-preset", "slow", 
				# Use High Quality
				"-crf", "20",
				# Reduce sound to stereo 
				"-ac", "2", 
				"-c:a", "libfdk_aac",
				"-y", # Overwrite all files automatically
				self.outfile],
				stdout = subprocess.DEVNULL,
				stderr = subprocess.DEVNULL
				)

		print ("Transcoding of %s started"%self.infile)	

	def abort(self):
		if self.process == None:
			return True
		if self.process.poll() == None:
			# Transcoding still in progress
			self.process.terminate()
			self.process.wait()
		
		# Remove any outfiles and reset
		os.remove(MPEG_PATH+self.outfile)

		self.reset()
		return True


	def scan(self):
		# Find a file to transcode
		# TODO Randomize the order of the list so that a single
		# problematic file does not hold up the transcoding line
		for f in os.listdir(self.path):
			# Only transcode mpeg files
			if f[-4:] != "mpeg":
				continue

			# Make sure there is not a capture ongoing
			if(self.capture_in_prgress(f[:-5])):
				continue
	
			self.infile = self.path+f
			self.start()
			return
			
	def capture_in_progress(self,title):	
		# Get a list of all tuners
		tuners = os.listdir(gdvr_config.database_path+"/tuners/")
		# Get a list of all files in the capture directory
		files = os.listdir(self.path)
	
		for t in tuners:
			# If a file matches the tuner ID, then that tuner
			# is currently recording
			if t in files:
				# Read that tuner file and see if the
				# title matches
				config = common.read_config(self.path+t)
				if config["title"] == title:
					# Title Matchs, so the recording
					# is in progress
					return True
		# No matches so this recording is not in progress
		return False

	def check(self):
		if self.process == None:
			# Nothing Going On, Scan for more work
			self.scan()
			return True
		retcode = self.process.poll()
		if retcode == None:
			# Transcoding in progress
			return True
		else:
			# TODO Analayze return code and dont delete 
			print("Transcoding of %s finished with code %d"
				%(self.infile,retcode))	
			# TODO Move MP4 to a different folder
			os.remove(self.infile)

			# Clear out the transcoder
			self.reset()

if __name__ == "__main__":

	t = Transcoder()

	while(1):
		t.check()
		

		time.sleep(60)

	


