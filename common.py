#!/usr/bin/env python

import configparser

def read_config(path):
	c = configparser.ConfigParser()
	f = open(path,"r")
	data = f.read()
	f.close()

	data = "[DEFAULT]\n\n"+data

	c.read_string(data)
	
	return c["DEFAULT"]

def write_config(data):
	pass
# In the fugure, this will be pulled from the /etc/ folder
database_path = "/mnt/raid/gDVR"	

required_subfolders = ["recordings", # Final Output folder of the DVR
			"episodes", # Episode Details pulled from Online DB
			"channels", # Channel Schedule pulled from Online DB
			"subscriptions", # Shows the user subscribes to
			"schedule", # upcoming recording events
			"capture", # Current Recordings
			"tuners"] # All tuners available to the DVR

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


# TODO Initialize the database folder structure if it does not existo already
"""
# Initialize if it does not exist
if (not os.path.exists(database_path)):
	os.mkdir(database_path)

for f in required_subfolders:
	p = database_path+"/"+f
	if (not os.path.exists(p)):
		os.mkdir(p)
		if f == "tuners":
			init_tuners()

# If any of these folder already exist, no initialization will be done
"""
