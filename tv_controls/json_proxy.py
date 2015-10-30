#!/usr/bin/env python

import asyncore
import socket

# This is the JSON_RPC Client.  Once the JSON_RPC_Server makes a connection, it
# will create an instance of this class to manage the connection. 
class JSON_RPC_Client(asyncore.dispatcher):

	def __init__(self, parent):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect( ("localhost",80) )
		self.buffer = ""
		self.parent = parent
	
	def send_raw(self,data):
		self.buffer += data

	def send_rpc(self,rpc_obj):
		# load_s the json object to a string
		# Generate HTTP header for the string
		self.send(data) 

	def handle_read(self):
		data = self.recv(9000)
		parent.send_raw(data)
		

class JSON_RPC_Handler(asyncore.dispatcher):

	def __init__(self,sock):
		asyncore.dispatcher.__init__(self,sock)
		self.outbox = ""
		self.inbox = ""
		self.client = JSON_RPC_Client(self)

	def handle_read(self):
		self.inbox += self.recv(9000)
		self.parse_inbox()

	def parse_inbox(self):
		# Check if an entire HTTP header is present
			# If not, continue and wait for more data
		# Parse COntent-Length to make sure entire payload was recieved
			# If not, continue and wait for mroe data
		# Parse path.  
			# If Path != jsonrpc, write all data to client
			self.client.send_raw(data)
			# if path == jsonrpc,
				obj = parse_json(self,body)
				if obj[??] == "SetVolume":
					# Block and send LIRC command isntead
				else:
					self.client.send_raw(data)

	def parse_json(self,data):
		
		


class JSON_RPC_Server(asyncore.dispatcher):
	pass


server = JSON_RPC_Server('localhost', 8080)
asyncore.loop()


# vim:tw=80
