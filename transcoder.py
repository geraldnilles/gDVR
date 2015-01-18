#!/usr/bin/env python


from twisted.internet import reactor, protocol, task
from twisted.protocols import basic
import subprocess
import os

MP4_PATH = "/mnt/raid/Recordings/"
MPEG_PATH = MP4_PATH+".mpeg/"

class transcoder:
	def __init__(self):
		self.reset()

	def reset(self):
		self.process = None
		self.infile = None
		self.outfile = None

	def start(self):
		if self.infile == None:
			return True
		# Remove the input extension and replace with mp4
		self.outfile = self.infile.rsplit(".",1)[0]+".mp4"
		
		self.process = subprocess.Popen(["ffmpeg", 
					# Specify Input File
					"-i",MPEG_PATH+self.infile, 
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
					MPEG_PATH+self.outfile],
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
		for f in os.listdir(MPEG_PATH):
			# Only transcode mpeg files
			if f[-4:] == "mpeg":
				self.infile = f
				self.start()
				return
			
			

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
			os.rename(MPEG_PATH+self.outfile,MP4_PATH+self.outfile)
			os.remove(MPEG_PATH+self.infile)

			# Clear out the transcoder
			self.reset()

class Handler(basic.LineReceiver):
	def lineReceived(self,cmd):
		
		args = cmd.decode("utf-8").split()
		ret = ""
		if args[0] == "status":
			ret = "Transcoding %s"%self.factory.transcoder.infile
		elif args[0] == "abort":
			self.factory.transcoder.abort()
			ret = "Aborted"
		else:
			ret = "%s is not a valid command"%(args[0])

		self.sendLine(bytes(ret,"utf-8"))

class Factory(protocol.ServerFactory):
	protocol = Handler

	def __init__(self):
		self.transcoder = transcoder()

	def check_transcoder(self):
		self.transcoder.check()

if __name__ == "__main__":

	f = Factory()

	reactor.listenTCP(9173,f)

	t = task.LoopingCall(f.check_transcoder)
	t.start(30)

	reactor.run()	
