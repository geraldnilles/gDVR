#!/usr/bin/env python

from twisted.internet import reactor, protocol, task
from twisted.protocols import basic
import json_protocol
import json

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
		elif args[0] in ["play","pause"]:
			# If no IP provided, select the first one on the list
			if(len(args) == 1):
				if len(self.factory.active_kodi_protocol_list) == 0:
					ip = None
				else:
					ip = self.factory.active_kodi_protocol_list[0]
			else:
				ip = self.ip_to_protocol(args[1])

			if ip == None:
				ret = "Provide IP not connected"
			else:
				ret = self.play(ip)
			
		elif args[0] == "listen":
			if(len(args) == 1):
				ips = self.factory.active_kodi_protocol_list
			else:
				ip = self.ip_to_protocol(args[1])
				if ip == None:
					ret = "IP not connected"
					ips = []
				else:
					ips = [ip]	
			for ip in ips:
				# Set the msg_callback to print everything 
				ip.msg_callback = self.string_callback
					
		elif args[0] == "status":
			# If no IP provided, select the first one on the list
			if(len(args) == 1):
				if len(self.factory.active_kodi_protocol_list) == 0:
					ip = None
				else:
					ip = self.factory.active_kodi_protocol_list[0]
			else:
				ip = self.ip_to_protocol(args[1])

			if ip == None:
				ret = "Provide IP not connected"
			else:
				ret = self.get_status(ip)


		# List all connected devices
		elif args[0] == "devices":
			ret = self.factory.kodi_list_devices()

		elif args[0] in ["load","open"]:
			# TODO Create a function to handle ip-based arguments
			# If no IP provided, select the first one on the list
			if(len(args) == 1):
				if len(self.factory.active_kodi_protocol_list) == 0:
					ip = None
				else:
					ip = self.factory.active_kodi_protocol_list[0]
			else:
				ip = self.ip_to_protocol(args[1])

			if ip == None:
				ret = "Provide IP not connected"
			else:
				ret = self.load(ip)
			

		elif args[0] == "":
			pass
		else:
			ret = "%s is not a valid command"%(args[0])

		self.send_string(ret)
	
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

	def create_base_msg(self):
		
		base_msg = {
			"jsonrpc":"2.0",
			"id":1,
		}
		return base_msg

	def get_status(self,p):
		msg = self.create_base_msg()
		msg["method"] = "Player.GetActivePlayers"

		p.msg_callback = self.status_callback
		p.sendMessage(msg)

	def status_callback(self,msg):
		if len(msg["result"]) == 0:
			ret = "Idle"
		else:
			ret = "Playing: "+str(msg["result"])
		self.send_string(ret)

	def play(self,p):
		msg = self.create_base_msg()
		msg["method"] = "Player.PlayPause"
		msg["params"] = {
					"playerid":1
				}

		# We dont really care about any call back for this
		#p.msg_callback = self.string_callback
		p.sendMessage(msg)
		self.send_string("PlayPause Toggled")

		
	def load(self,p):
		msg = self.create_base_msg()
		msg["method"] = "Player.Open"
		msg["params"] = {"item": {
						"file":"nfs://192.168.0.200/srv/nfs4/media/Movies/Features/Lucy.mkv"
					}
				}
 
		"""
				{
					"item":"nfs://192.168.0.200/srv/nfs4/media/Movies/Features/Lucy.mkv"
				}
		"""

		# We dont really care about any call back for this
		p.msg_callback = self.string_callback
		p.sendMessage(msg)
		self.send_string("Video Opened")


	def string_callback(self,msg):

		ret = json.dumps(msg);
		self.send_string(ret)

		return self.string_callback
		

	def send_string(self,s):
		if s == None or s == "":
			return
		self.sendLine(bytes(s,"utf-8"))
		
	

	def ip_to_protocol(self,ip):
		for d in self.factory.active_kodi_protocol_list:
			if d.transport.getPeer().host == ip:
				return d

		return None


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


