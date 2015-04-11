#!/usr/bin/env python

import configparser

def read_config(path):
	c = configparser.ConfigParser()
	f = open(path,"r")
	data = f.read()
	f.close()

	data = "[DEFAULT]\n\n"+data

	c.read_string(data)
	
	return c.["DEFAULT"]

def write_config(data):
	pass
