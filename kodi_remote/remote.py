#!/usr/bin/env python

from twisted.internet import reactor, protocol, task
from twisted.protocols import basic
import json_protocol

# Handles Socket Requests
class Handler(basic.LineReceiver):
	def lineReceived(self, cmd):
		# TODO Switch to lowercase
		# Separate by Whitespace
		args = cmd.decode("utf-8").split()
		ret = ""
		# Connect to the provided IP or all IPs
		if args[0] == "connect":
			ret = self.connect(args)
		# Search for media that matches the provided string
		elif args[0] == "search":
			pass
		elif args[0] == "play":
			pass
		elif args[0] == "status":
			pass
		# List all connected devices
		elif args[0] == "devices":
			ret = self.factory.kodi_list_devices()
		elif args[0] == "":
			pass
		else:
			ret = "%s is not a valid command"%(args[0])

		self.sendLine(bytes(ret,"utf-8"))
	
	def connect(self,args):
		ips = []
		if len(args) == 1:
			ips = self.factory.kodi_ip_list
		if len(args) > 1:
			ips = args[1:]

		if len(ips) == 0:
			return "Nothing to connect"
		out = "Connecting to ..."
		for ip in ips:
			# TODO See if a connection is already present
			# Connect if not
			reactor.connectTCP(ip,9090,
				self.factory.kodi_factory)
			out += "\n"+ip
		return out

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
		self.kodi_ip_list = ["FamilyRoom","BedroomMedia"]
		
	def kodi_started(self,protocol):
		print("Connection Started")
		if protocol not in self.active_kodi_protocol_list:
			self.active_kodi_protocol_list.append(protocol)

	def kodi_stopped(self,protocol):
		print("Connection Stopped")
		if protocol in self.active_kodi_protocol_list:
			self.active_kodi_protocol_list.remove(protocol)

	def kodi_list_devices(self):
		out = "Connected Kodi Devices:\n"
		for d in self.active_kodi_protocol_list:
			out += str(d.transport.getPeer())
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


