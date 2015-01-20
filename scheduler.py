#!/usr/bin/env python


from twisted.internet import reactor, protocol, task
from twisted.protocols import basic
import dateutil.parser
import time

# Scheduler
#
# This class will maintain an agenda (list of recording events).  A 
# periodic callback function will be used to monitor the agenda and
# trigger recordings.
class scheduler:
	# Initialize the agenda
	def __init__(self):
		self.agenda = []

	# Start capturing video
	# Returns True if the capture was started succesfully.
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

	def read_configs(self):
		# List to hold the manual shows
		shows = []
		for path in ["./gdvr.conf", #Current Directory
				"~/.gdvr.conf", # Home Directory
				"/etc/gdvr.conf"]: # Global Dir
			# Existance Check
			if not os.path.exists(path):
				continue
			# Read Conf file and store data into disct
			c = configparser.ConfigParser()
			c.read(path)
			for sec in c.sections():
				# We only care about manual scheduling
				if c[sec]["type"] == "manual":
					s = {}
					for i in c[sec]:
						s[i] = c[sec][i]
					s["title"] = sec
					shows.append(s)
		self.parse_conf(shows)
		return False

	# Convers the conf file data into a usable start time
	def parse_configs(self,shows):
		for s in shows:
			# Parse the repeat string and convert to a list
			# of days in the week
			dows = []
			for char in s["repeat"]:
				dows.append(int(char))
			
			# Get current day of the week
			today = datetime.date.today()
			# Also get tomrrow so we can plan ahead
			tomorrow = today+datetime.timedelta(days=1)

			start_unix_times = []
			for d in [today,tomorrow]:
				# If the day is not part of the repeat
				# string, skip it
				if d.weekday() not in dows:
					continue
				# Create an empty event object
				event = {}
				# Generate the start time float
				day_str = d.strftime("%A")
				dt = dateutil.parser.parse(day_str+" "
					+s["start_time")
				event["start_time"] = dt.timestamp()	
				# Generate the title name
				event["name"]=d.strftime(s["title"]
						+"-%b_%d.mpeg")
				# Generate Duration 
				dur_str = s["duration"].strip
				base = 0
				multiplier = 0
				if(dur_str[-1] in ["H","h"]:
					base=float(dur_str[:-1])
					multipler = 60*60
				elif(dur_str[-1] in ["M","m"]:
					base=float(dur_str[:-1])
					multiplier = 60
				elif(dur_str[-1] in ["S","s"]:
					base=float(dur_str[:-1])
					multiplier = 1
				else:
					base=float(dur_str)
					multiplier = 1
				# TODO Allow for "hour" "Min" ...
				event["duration"] = base*multiplier	

				# Copy in other detials
				event["channel"] = s["channel"]
				
				
				
				# Check if it is already schedule
				exists = False
				for a in self.agenda:
					if a["name"] == event["name"]:
						exists = True
				if exists:
					continue

				# Check that the start time is not old
				if event["start_time"] > time.time():
					continue

				# All checks pass
				# Add the new event to the agenda
				self.agenda.append(event)

	def check(self):
		to_remove = []
		# TODO Sort by Priority
		for event in self.agenda:
			# Attempt to kick of a stream capture
			# If returns True, then this event
			if self.start_capture(a)
				to_remove.append(a)	
		# Remove the events that are done	
		for events in to_remove:
			self.agenda.remove(events)


class Handler(basic.LineReceiver):
	def lineReceived(self,cmd):
		pass

class Factory(protocol.ServerFactory):
	protocol = Handler

	def __init__(self):
		# Generate a Scheduler object
		self.scheduler = scheduler()

	def check_schedule(self):
		# Check the Scheduler
		self.scheduler.check()

	def update_config(self):
		self.scheduler.read_configs()


if __name__ == "__main__":

	f = Factory()
	reactor.listenTCP(9174,f)
	# Reload the config files every hour so modifications can be made	
	t1 = task.LoopingCall(f.update_config())
	t1.start(60*60)
	# Check the schedule every 10 seconds.
	t2 = task.LoopingCall(f.check_schedule())
	t2.start(10)
	
	reactor.run()

