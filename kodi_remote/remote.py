#!/usr/bin/env python

from twisted.internet import reactor, protocol, task
from twisted.protocols import basic
import json_protocol
import json
import os
import shlex
import argparse


# Handles Socket Requests
class Handler(basic.LineReceiver):

	def lineReceived(self, cmd):
		# TODO Switch to lowercase
		# TODO User Arg Parser to clean this up
		# Separate by Whitespace
		args = shlex.split(cmd.decode("utf-8"))

		parser = argparse.ArgumentParser()
		parser.add_argument("-p","--play","--pause",
				action="store_true")	
		parser.add_argument("-i","--ip", metavar="address")
		parser.add_argument("-c","--connect", action="store_true")
		parser.add_argument("-s","--search", metavar="query")
		parser.add_argument("-k","--seek", metavar="percent")
		parser.add_argument("-t","--stop", action="store_true")
		parser.add_argument("-l","--listen", action="store_true")
		parser.add_argument("-a","--status", action="store_true")
		parser.add_argument("-b","--button", metavar="button")
		parser.add_argument("-d","--devices", action="store_true")
		parser.add_argument("-r","--random", metavar="tv show")
		parser.add_argument("-n","--number", 
					metavar="number of episodes")
		parser.add_argument("-o","--load","--open", 
				metavar="query")
		
		try:
			pargs = parser.parse_args(args)
		except:	
			ret = parser.format_help()
			self.send_string(ret)
			return

		ret = ""
		# Connect to the provided IP or all IPs
		if pargs.connect:
			ret = self.connect(pargs)
		# Search for media that matches the provided string
		elif pargs.search:
			ret = self.search(pargs)
		elif pargs.play:
			ret = self.play(pargs)
			
		elif pargs.stop:
			ret = self.stop(pargs)
			
		elif pargs.seek:
			ret = self.seek(pargs)

		elif pargs.listen:
			#ip.msg_callback = self.string_callback
			self.listen(pargs)
					
		elif pargs.status:
			ret = self.status(pargs)

		# List all connected devices
		elif pargs.devices:
			ret = self.factory.kodi_list_devices()

		elif pargs.load:
			ret = self.load(pargs)	

		elif pargs.random:
			ret = self.random(pargs)	

		elif pargs.button:
			ret = self.button(pargs)	

		else:
			ret = parser.format_help()

		self.send_string(ret)
	
	def connect(self,args):
		ips = []
		# If no Ip was given, select all
		if args.ip == None:
			ips = self.factory.kodi_ip_list
		else:
			ips.append(args.ip)

		if len(ips) == 0:
			return "Nothing to connect"
		out = "Connecting to ...\n"
		for ip in ips:
			# TODO See if a connection is already present
			# Need to figure out a way that translates DNS
			# names to IP addreesses first
			# Connect if not
			reactor.connectTCP(ip,9090,
				self.factory.kodi_factory)
			out += "\n"+ip
		return out

	def create_base_msg(self):
		
		base_msg = {
			"jsonrpc":"2.0",
			"id":1,
		}
		return base_msg

	def status(self,args):
		msg = self.create_base_msg()
		msg["method"] = "Player.GetActivePlayers"

		p = self.get_protocol(args)
		if p == None:
			return "IP Not connected"

		p.msg_callback = self.status_callback
		p.sendMessage(msg)

	def status_callback(self,msg):
		if len(msg["result"]) == 0:
			ret = "Idle"
		else:
			ret = "Playing: "+str(msg["result"])
		self.send_string(ret)

	def play(self,args):
		msg = self.create_base_msg()
		msg["method"] = "Player.PlayPause"
		msg["params"] = {
					"playerid":1
				}

		p = self.get_protocol(args)
		if p == None:
			return "IP Not connected"

		p.sendMessage(msg)
		self.send_string("PlayPause Toggled")

	def stop(self,args):
		msg = self.create_base_msg()
		msg["method"] = "Player.Stop"
		msg["params"] = {
					"playerid":1
				}

		p = self.get_protocol(args)
		if p == None:
			return "IP Not connected"

		p.sendMessage(msg)
		self.send_string("Stopped")

	def seek(self,args):

		if args.seek == None:
			return "Seek Percentage Not Provided"

		msg = self.create_base_msg()
		msg["method"] = "Player.Seek"
		msg["params"] = {
					"playerid":1,
					"value":float(args.seek)
				}

		p = self.get_protocol(args)
		if p == None:
			return "IP Not connected"

		
		p.sendMessage(msg)
		self.send_string("Seek to %s percent"+args.seek)

	# Play a random set of episodes
	def random(self,args):
		# Find Directory from Query
		shows = self.find_tv_shows(args)
		if(len(shows) == 0):
			return "Could not %s on the server"%args.random
		if(len(shows) > 1):
			return ("Too Many Shows match the query "
					+repr(shows))
		# Figure out how many episodes to play
		num_play = 3
		if args.number:
			num_play = int(args.number)
			if num_play < 1:
				num_play = 3		


		# Get a sorted list
		episodes = sorted(os.listdir(self.tv_path+shows[0]))

		if num_play > len(episodes):
			num_play = len(episodes)
		
		# Pick a random point in the list
		start_index = random.randint(0,len(episodes)-num_play)
		# Set the stop point
		stop_index = start_index + num_play
		# Add the paths to the playlist
		for e in episodes[start_index:stop_index]:
			self.playlist.append(self.tv_directory+shows[0]+"/"+e) 

		msg = self.create_base_msg()
		msg["method"] = "Player.Open"
		msg["params"] = {"item": {
					"file":("nfs://192.168.0.200"
						+self.playlist.pop())
					}
				}
 
		p = self.get_protocol(args)
		if p == None:
			return "IP Not connected"

		# We dont really care about any call back for this
		p.msg_callback = self.string_callback
		p.sendMessage(msg)
		self.send_string("Playlist Started")
	
	playlist = []
	# NOTE: This wont work.  It requires that this Handler class stay
	# alive. And we cant expect that to be true.  It would be better if
	# the playlist were embedded int the Main Factory, or in the Kodi 
	# protocol instance, or in a separate daemon
	def playlist_callback(self,proto,msg):
		# Check Message Type.
		if msg["method"] == "Player.OnStop":
			new_msg = self.create_base_msg()
			new_msg["method"] = "Player.Open"
			new_msg["params"] = {"item":{"file":(
					"nfs://192.168.0.200"
					+self.playlist.pop())
					}
				}
			proto.sendMessage(new_msg)
			self.send_string("Next Item Playing")
	
		
	def load(self,args):

		if args.load == None:
			return "No Video Provided to load"
		
		# Find the video on the file system. 
		matches = self.find_movies(args.load) 
		if len(matches) == 0:
			return "Could not find %s on the server"%args.load
		if len(matches) > 1:
			return "Query not specific enough: %s"%repr(matches)


		msg = self.create_base_msg()
		msg["method"] = "Player.Open"
		msg["params"] = {"item": {
					"file":("nfs://192.168.0.200"
						+self.movie_directory
						+matches[0])
					}
				}
 
		p = self.get_protocol(args)
		if p == None:
			return "IP Not connected"

		# We dont really care about any call back for this
		#p.msg_callback = self.string_callback
		p.sendMessage(msg)
		self.send_string("Video Opened")

	def button(self,args):

		p = self.get_protocol(args)

		msg = self.create_base_msg()

		if args.button == "up":
			msg["method"] = "Input.Up"
		elif args.button == "down":
			msg["method"] = "Input.Down"
		elif args.button == "left":
			msg["method"] = "Input.Left"
		elif args.button == "right":
			msg["method"] = "Input.Right"
		elif args.button == "back":
			msg["method"] = "Input.Back"
		elif args.button == "select":
			msg["method"] = "Input.Select"

		p.sendMessage(msg)
		self.send_string("Command %s sent"%args.button)
	

	# Listen to TCP traffic from one or all Kodi devices and print
	# packets to the screen.
	def listen(self,args):
		protos = []
		# If ip provided, attempt to find it and add it to the
		# proto list
		if args.ip:
			p = self.get_protocol(args)
			if p:
				protos.append(p)
		# If no ip provided, add all connected devices to the 
		# proto list.
		else:
			protos = self.factory.active_kodi_protocol_list

		# For all protocols, assign the "string_callback" so 
		# that all data is printed
		for p in protos:
			p.msg_callback = self.string_callback


	def string_callback(self,msg):

		ret = json.dumps(msg);
		self.send_string(ret)

		return self.string_callback
		

	def send_string(self,s):
		if s == None or s == "":
			return
		self.sendLine(bytes(s,"utf-8"))
		
	

	def get_protocol(self,args):
		if args.ip == None:
			return self.factory.active_kodi_protocol_list[0]

		for d in self.factory.active_kodi_protocol_list:
			if d.transport.getPeer().host == args.ip:
				return d

		return None

	def search(self,args):
		show_movies = self.find_movies(args.search)
		ret = "Movies:\n"
		for m in show_movies:
			ret += "  %s\n"%(m[:-4])

		return ret
		

	movie_directory = "/srv/nfs4/media/Movies/Features/"
	def find_movies(self,query):
		all_movies = sorted(os.listdir(self.movie_directory))
		show_movies = [] 
		limit = 20
		for m in all_movies:
			# Stop loop if limit is hit
			if len(show_movies) > limit:
				break
			# Ignore Hidden Files
			if m[0] == ".":
				continue
			# Ignore all but MKVs
			if m[-4:] != ".mkv":
				continue
			# If not query, match all
			if(query == ""):
				show_movies.append(m)
				continue
			# Look if query is contained in this movie
			if(query.lower() in m.lower()):
				show_movies.append(m)

		return show_movies


class KodiFactory(json_protocol.Factory):
	def buildProtocol(self,addr):
		#
		print ("Connecting to ",addr)
		#
		self.resetDelay()
		# Generate a Protocol Instance
		p = json_protocol.Protocol()
		# Reference the protocol back to this factory
		p.factory = self
		# Register the protocol with the Main factory
		self.factory.kodi_register(p)
		return p

# Waits for Socket Connections and dispatches Handlers		
class Factory(protocol.ServerFactory):	
	# Specify the class that will handle new connections
	protocol = Handler

	def __init__(self):
		print("Creating Telnet Factory")
		# Create a JSON factory
		self.kodi_factory = KodiFactory()
		# Add this Factory to the JSON factory so changes can
		# be communicated
		self.kodi_factory.factory = self
		# A list of All Kodi Protocols
		self.kodi_protocol_list = [] 
		# A list of Active Kodi Protocols
		self.active_kodi_protocol_list = []
		# A list of all IPs/Hostnames to try to connect to
		self.kodi_ip_list = ["FamilyRoom"]
		
	def kodi_started(self,protocol):
		print("Connection Started Callback")
		if protocol not in self.active_kodi_protocol_list:
			self.active_kodi_protocol_list.append(protocol)

	def kodi_stopped(self,protocol):
		print("Connection Stopped")
		if protocol in self.active_kodi_protocol_list:
			self.active_kodi_protocol_list.remove(protocol)

	def kodi_list_devices(self):
		out = "Connected Kodi Devices:\n"
		for d in self.active_kodi_protocol_list:
			out += "  "
			out += d.transport.getPeer().host
			out += "  "
			out += d.transport.getHost().host
		return out
			

	# Register a protocol with this main factory 
	def kodi_register(self,protocol):
		print ("Registering Protocol")
		if protocol not in self.kodi_protocol_list:
			self.kodi_protocol_list.append(protocol)
			protocol.stop_callback = self.kodi_stopped
			protocol.start_callback = self.kodi_started


if __name__ == "__main__":


	# Initiate the factory
	f = Factory()
	# Open a Socket for communication
	reactor.listenTCP(9175,f)

	reactor.run()


