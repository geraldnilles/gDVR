#!/usr/bin/env python

from twisted.internet import reactor
from twisted.web.http import HTTPFactory, HTTPChannel, Request

import os, json
import http.client

class Remote:
	
	def __init__(self):
		self.devices = []
		self.hostnames = ["FamilyRoom","BedroomMedia"]

		# Internal Path to Media Folder 
		self.local_root = "/mnt/raid/"
		# NFS Path to Media Folder
		self.remote_root = "nfs://192.168.0.200/media/"

	# Look for all Kodi devices in the network.
	def discover(self):
		self.devices = []
		for h in self.hostnames:
			# Check if device is powered on
			try:
				self.get_status(h)
				self.devices.append(h)
			except:
				pass
	
	def create_json_obj(self):
		return {
			"jsonrpc":"2.0",
			"id":1
			}

	# Add Item to Playlist
	def add_to_playlist(self,ip,path):
		pass

	# Play Device
	def play(self,ip):
		pass

	# Pause Device
	def pause(self,ip):
		pass

	# Stop Device 
	def stop(self,ip):
		pass

	def get_playlist(self,ip):
		pass

	def get_status(self,ip):
		req = self.create_json_obj()
		req["method"] = "Player.GetActivePlayers"
		return self.http(ip,req)

	def get_playlistid(self,ip):
		req = self.create_json_obj()
		req["method"] = "Playlist.GetPlaylists"
		resp = self.http(ip,req)
		for p in resp["result"]:
			if p["type"] == "video":
				return p["playlistid"]
		return None

	def get_playlist_items(self,ip):
		pid = self.get_playlistid(ip)
		req = self.create_json_obj()
		req["method"] = "Playlist.GetItems"
		req["params"] = {"playlistid": pid}
		return self.http(ip,req)

	# Send and Recive JSON over HTTP
	def http(self,ip,msg):
		headers = {"Content-Type":"application/json"}
		conn = http.client.HTTPConnection(ip,timeout=2)
		conn.request("POST","/jsonrpc",json.dumps(msg),headers)
		resp = conn.getresponse()
		data = resp.read()
		conn.close()
		return json.loads(data.decode("utf-8"))

class RequestHandler(Request):

	def setByteHeader(self,a,b):
		self.setHeader(bytes(a,"utf-8"),bytes(b,"utf-8"))
	

	def process(self):
		self.setByteHeader("Content-Type","text/plain")
		msg = "Unknown Command"

		cmd = self.path.decode("utf-8")[1:].lower().split("/")[1:]
	
		if cmd[0] == "watch":
			if len(cmd) == 2:
				self.channel.factory.streamer.watch_channel(cmd[1])
				msg = "OK"

		if cmd[0] == "stop":
			self.channel.factory.streamer.stop()
			msg = "OK"

		if cmd[0] == "status":
			msg = self.channel.factory.streamer.status()

		if cmd[0] == "sling":
			self.channel.factory.streamer.sling_to_xbmc(cmd[1])
			msg = "OK"

	
		self.write(bytes(msg,"utf-8"))

		self.finish()


class Handler(HTTPChannel):
	requestFactory = RequestHandler



class Factory(HTTPFactory):
	protocol = Handler

	def __init__(self):
		super(Factory,self).__init__()
		self.remote = Remote()

if __name__ == "__main__":

	"""
	f = Factory()
	
	reactor.listenTCP(9178,f)
	print ("gDVR Kodi Remote Started")
	reactor.run()
	"""

	r = Remote()
	print(r.get_status("FamilyRoom"))
	print(r.get_playlist_items("FamilyRoom"))


