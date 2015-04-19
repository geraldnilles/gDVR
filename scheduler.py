#!/usr/bin/env python


import time
import common

class Scheduler:
	# Initialize the agenda
	def __init__(self):
		self.path = commong.database_path+"/schedule/"

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

	# Convers the conf file data into a usable start time
	def check(self):
		for f in os.listdir(self.path):
			event = common.read_config(path+f)

			# Check if we should be recording this file
			if(self.is_ready(event) and 
					not self.is_recording(event)):
				self.start_recording(config)
			# If file is stlae
			if(self.is_stale(event)):
				os.remove(self.path+f)

	def calc_duration(self,duration):
		# Generate Duration 
		dur_str = duration.strip()
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

		return base*multiplier

	def calc_time(self,time):
		pass

	def ready(self,event):
		# If a recurring event...
		if "day_of_week" in event:
			# Is today in the day of week
			today = datetime.date.today()
			if today_dow not in dows:
				return False

			new = time.time()
			start = self.calc_time()
			end = start + self.calc_duration(event["duration"])
			if(now >= start and now <= end):
				return True
			
		else:
			now = time.time()
			start = int(event["start_time"])
			if "end_time" in event:
				end = int(event["end_time"])
			else:
				end = start + self.calc_duration(
					event["duration"])

			if(now >= start and now <= end):
				return True

		return False
				

	def parse(self,event):
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




if __name__ == "__main__":
	s = Scheduler()
	while(1):
		s.check()
		time.sleep(10)

