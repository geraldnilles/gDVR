#!/usr/bin/env python


from twisted.internet import reactor, protocol, task
from twisted.protocols import basic

class Handler(basic.LineReceiver):
	def lineReceived(self,cmd):
		pass

class Factory(protocol.ServerFactory):
	protocol = Handler

	def __init__(self):
		# A list of scheduled recording tuples
		self.agenda = []

	def start_capture(self,event):
		if event["start_time"]+event["duration"] < time.time():
			# Event is very old.
			# Return true so it is removed from the schedule
			return True

		elif time.time() > event["start_time"]:
			# Event is ripe and ready for catpure
			if capture.start(event["name"],
					event["duration"],
					event["channel"]):
				# Capture Started Succesfully
				return True
			else:
				# Something went wrong trying to start the
				# capture.  
				# TODO Print to stderr instead of stderr
				print ("Could not start capturing %s"%
						(event["name"]))
				# Attempt to manage the conflict and return
				# the result.
				return self.manage_conflict(event)
		else:
			# Event is not ready to kick off
			return False
		
	def manage_conflict(self,event):
		# Eventaully, id like to look at the priority of the current 
		# recordings and decide if we need to cut off one of the 
		# in-progress recordings.  But for now, we will just cancel
		# all recordings by returning True
		return True


	def check_schedule(self):
		to_remove = []
		# TODO Sort by Priority
		for event in self.agenda:
			# Attempt to kick of a stream capture
			# If returns True, then this event
			if start_capture(a)
				to_remove.append(a)	
	
		for events in to_remove:
			self.agenda.remove(events)

	def load_config(self):
		for path in ["./gdvr.conf", #Current Directory
				"~/.gdvr.conf", # Home Directory
				"/etc/gdvr.conf"]: # Global Dir
			if os.path.exists(path):
				conf = ...
				
				return True
		return False


if __name__ == "__main__":

	f = Factory()
	reactor.listenTCP(9174,f)
	
	t1 = task.LoopingCall(f.load_config())
	t1.start(60*60)

	t2 = task.LoopingCall(f.check_schedule())
	t2.start(10)
	
	reactor.run()

