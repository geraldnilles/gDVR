#!/usr/bin/env python

from twisted.internet import reactor, protocol
from twisted.protocols import basic
import subprocess

# TODO MOve into a config file
MPEG_PATH = "/mnt/raid/Recordings/.mpeg/"

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

		self.process = subprocess.Popen([
					"hdhomerun_config",
					self.id,
					"save",
					str(self.number),
					MPEG_PATH+self.temp_name
				])

	def stop(self):
		self.process.kill()
		os.rename(MPEG_PATH+self.temp_name,MPEG_PATH+self.name)
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
			return False

# Handles Socket Requests
class Handler(basic.LineReceiver):
	def __init__(self,tuners):
		self.tuners = tuners

	def lineReceived(self, cmd):
		# TODO Switch to lowercase
		# Separate by Whitespace
		args = cmd.split()
		ret = ""
		if args[0] == "status":
			ret = self.status(args)
		if args[0] == "start":
			ret = self.start(args)
		if args[0] == "stop":
			ret = self.stop(args)

		self.sendLine(ret)
		self.transport.loseConnection()

	def status(self,args):
		report = []
		output = ""
		if len(args) == 1:
			report = self.tuners
		
		else:
			for a in args[1:]:
				for t in self.tuners:
					if t.number == a:
						report.append(t)
		for t in report:
			output += t.number		
			output += "\n"
		return output

	def start(args):
		for t in self.tuners:
			if t.is_available():
				t.start(args[1],args[2],args[3])
				return "Recording Started on Tuner %s %d"%(
						t.id, t.number)
		else:
			return "No Tuners Available"

	def stop(args):
		stop = []
		output = ""
		if args[1] == "all":
			stop = self.tuners
		else:
			for a in args[1:]:
				for t in self.tuners:
					if t.number == a:
						stop.append(t)

		for t in stop:
			t.stop()

# Waits for Socket Connections and dispatches Handlers		
class Factory(protocol.ServerFactory):			
	def buildProtocol(self):
		return Handler(self.tuners)
		

	def check_tuners(self):
		for t in self.tuners()
			t.check_up()

	def init_tuners(self):
		self.tuners = []

	def register_tuner(self,id,number):
		self.tuners.append(tuner(id,number))

if __name__ == "__main__":
	f = Factory()
	f.register_tumer("id",0)
	f.register_tumer("id",1)
	f.register_tumer("id",2)
	reactor.listenUNIX("/tmp/gdvr.capture",Factory())
	reactor.Task("1 minute",f.check_tuners())
	reactor.run()





