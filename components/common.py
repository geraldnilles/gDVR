#!/usr/bin/env python

import configparser
import os

database_path = "~/.gDVR"

required_subfolders = ["recordings", # Final Output folder of the DVR
			"episodes", # Episode Details pulled from Online DB
			"channels", # Channel Schedule pulled from Online DB
			"subscriptions", # Shows the user subscribes to
			"schedule", # upcoming recording events
			"capture", # Current Recordings
			"tuners"] # All tuners available to the DVR



def duration_2_endtime(duration,start_time=None):
	if start_time == None:
		start_time = time.time()

	m = re.search("^\s*([0-9\.]+)\s*([mMsShH]*)",duration)
	if m:
		base = float(m.group(1))
		multiplier = 1
		suffix = m.group(2)
		if suffix[0] in ["s","S"]:
			# already in seconds, set multiplier to 1
			multiplier = 1
		elif suffix[0] in ["m","M"]:
			# minutes, set multiplier to 60
			multiplier = 60
		elif suffix[0] in ["H","h"]:
			# hours, set multiplier to 3600
			multiplier = 60*60

		return start_time + base*multiplier 
	else:
		return None
	

def read_config(path):
	c = configparser.ConfigParser()
	f = open(path,"r")
	data = f.read()
	f.close()

	data = "[DEFAULT]\n\n"+data

	c.read_string(data)
	
	out = {}

	for key in c["DEFAULT"]:
		out[key] = c["DEFAULT"][key]

	return out

def write_config(path,data):
	out = ""
	for key in data:
		out += key+": "+str(data[key])+"\n"

	f = open(path,"w")
	f.write(out)
	f.close()


# Shoudl only be called if the tuners files dont already exist
def init_tuners():
	"""
	hdhomerun_config discover
	get each device on the network
	for each device, count the number of tuners and make an ID for each
	"""	
	pass


# Generates a full-path list for the given subdirectory
def full_path_list(subdir):
	out = []
	for x in short_path_list(subdir):
		out.append(database_path+"/"+subdir+"/"+x)

	# TODO Verify that these are not folders

	return out
		

def short_path_list(subdir):
	if subdir not in required_subfolders:
		return []
	return os.listdir(database_path+"/"+subdir)


def sub_path(subdir):
	return database_path+"/"+subdir+"/"


def check_database():
	if (not os.path.exists(database_path)):
		os.mkdir(database_path)

	for f in required_subfolders:
		p = database_path+"/"+f
		if (not os.path.exists(p)):
			os.mkdir(p)
			if f == "tuners":
				init_tuners()

config_path = "/etc/gdvr.conf"

# Initialize the database if needed
if os.path.exists(config_path):
	# Read the configured path from the file
	x = read_config(config_path)
	database_path = x["database_path"]

# We probably want to find a better way to decide when to check the database
# instead of running it every time common is imported.
check_database()

