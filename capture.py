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

	# Resets all variables to the default values	
	def reset(self):
		self.name = None
		self.stop_time = None
		self.start_time = None
		self.temp_name = None
		if self.process.poll == None:
			self.process.terminate()
		self.process.wait()
		self.process = None

	def start(self,name,start_time,duration,channel):
		# TODO Check if name already exists
		
		self.name = name
		self.start_time = time.time()
		self.temp_name = self.name+".temp"
		# TODO Convert duration to seconds if a string prefix
		# so a string of "20m" ==> 20*60
		self.stop_time = self.start_time + duration
		# Change Channel
		subprocess.call(["hdhomerun_config",
					self.id,
					"set",
					"/tuner%d/vchannel",
					channel])
		# Start Capture and store the process object
		self.process = subprocess.Popen([
					"hdhomerun_config",
					self.id,
					"save",
					str(self.number),
					MPEG_PATH+self.temp_name
				])
	
	## Stops capturing and moves the file from temp location to the
	# actual location
	def stop(self):
		# Send the terminate call
		self.process.terminate()
		# Wait for it to end
		# TODO Add a Timeout afterwhich you try to "kill" it
		self.process.wait()
		# Move the temp_name to the actual name
		os.rename(MPEG_PATH+self.temp_name,MPEG_PATH+self.name)
		# Reset all the tuner variables
		self.reset()

	# Returns a string summarizing the tuner's status
	def status_string(self):
		template = """Device ID: {did} Tuner #: {number}
\t{state}
"""
		state = ""
		if self.is_available():
			state = "Available"
		else:
			state = "Currently Recording %s"%(self.name)

		return template.format(did=self.id,number=self.number,state=state)

	def is_available(self):
		if name == None:
			return True
		else:
			return False

	# Check if the recording needs to stop or make sure the process
	# did not die prematurely 
	def check_up(self):
		# If the tuner is idle, return
		if name == None:
			return True
		# Check if the capture is done, stop and return
		if time.time() > self.stop_time:
			self.stop()
			return True
		# If the capture is still ongoing, Return
		if self.process.poll()==None:
			return True
		# If the catpure stopped unexptectedly, Print and error
		else:
			# TODO Print to StdErr and log it
			print ("Tuner %d quit prematurely"%self.number)	
			# Reset the tuner
			self.reset()
			return False

# Handles Socket Requests
class Handler(basic.LineReceiver):
	def lineReceived(self, cmd):
		# TODO Switch to lowercase
		# Separate by Whitespace
		args = cmd.split()
		ret = ""
		if args[0] == "status":
			for t in self.factory.tuners:
				ret += t.status_string()
		if args[0] == "start":
			ret = self.start(args)
		if args[0] == "stop":
			ret = self.stop(args)

		self.sendLine(ret)
		#self.transport.loseConnection()
	
	# Looks for an available tuner and starts recording
	def start(args):
		for t in self.factory.tuners:
			if t.is_available():
				t.start(args[1],args[2],args[3])
				return "Recording Started on Tuner %s %d"%(
						t.id, t.number)
		else:
			return "No Tuners Available"

	# Stop a recording early
	def stop(args):
		if len(args) == 1:
			return "No recording specified.  No recordings stopped"
		
		if args[1] == "all":
			for t in self.factory.tuners:
				t.stop()
			return "All Recordings Stopped"
		else:
			for t in self.factory.tuners:
				if t.name == arg[1]:
					t.stop()
			return "Recording stopped: %s",(args[1])

# Waits for Socket Connections and dispatches Handlers		
class Factory(protocol.ServerFactory):	
	# Specify the class that will handle new connections
	protocol = Handler

	# Initialize the Tuner LIst
	def __init__(self):
		self.tuners = []
	
	# Checkup on each tuner
	def check_tuners(self):
		for t in self.tuners()
			t.check_up()
	
	# Register a Tuner with the class
	def register_tuner(self,id,number):
		self.tuners.append(tuner(id,number))

	# TODO Auto Register tuners using the discovery command

if __name__ == "__main__":
	f = Factory()
	f.register_tumer("id",0)
	f.register_tumer("id",1)
	f.register_tumer("id",2)
	reactor.listenUNIX("/tmp/gdvr.capture",Factory())
	reactor.Task("1 minute",f.check_tuners())
	reactor.run()





