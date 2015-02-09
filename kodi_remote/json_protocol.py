#!/usr/bin/env python

from twisted.internet import reactor, protocol

import os, json

class Protocol(protocol.Protocol):
	def __init__(self):
		self.buffer = ""
		self.inbox = []
		self.stop_callback = None
		self.start_callback = None

	def dataReceived(self,data):
		self.buffer += data.decode("utf-8")
		print(self.buffer)
		self._parseBuffer()

		while(len(self.inbox) > 0):
			self.messageReceived(self.inbox.pop(0))

	def _parseBuffer(self):
		open_count = 0
		close_count = 0
		border_indices = [-1]
		for i in range(len(self.buffer)):
			if self.buffer[i] == '{':
				open_count += 1
			if self.buffer[i] == '}':
				close_count += 1

			if(open_count == close_count 
				and open_count != 0):
				border_indices.append(i)
		
		for i in range(len(border_indices)-1):
			start = border_indices[i]+1
			stop = border_indices[i+1]+1
			json_str = self.buffer[start:stop]
			print("Decoding",json_str)
			self.inbox.append(json.loads(json_str))

		# Chop off rest of buffer
		self.buffer = self.buffer[border_indices[-1]+1:]
	
	def messageReceived(self,msg):
		# To be Overwitten with Recieved Message
		print(msg)

	def sendMessage(self,msg):
		self.transport.write(bytes(json.dumps(msg),"utf-8"))

	def connectionMade(self):
		print ("Connection Made!")
		self.sendMessage({
				"jsonrpc":"2.0",
				"id":1,
				"method":"Player.GetActivePlayers"
			})

		if (self.start_callback != None):
			# Run the Start Callback function
			self.start_callback(self)

		#self.local_root = "/mnt/raid/"
		# NFS Path to Media Folder
		#self.remote_root = "nfs://192.168.0.200/srv/nfs4/media/"

	def connectionLost(self,reason):
		print("Connection Lost!")
		if (self.stop_callback!= None):
			# Run the Stop Callback
			self.stop_callback(self)


class Factory(protocol.ReconnectingClientFactory):
	protocol = Protocol

	# Longest delay between retries will be 2 minutes
	maxDelay = 64
	# Initial delay of 2 seconds
	initialDelay = 2
	# Delay multiplied by 2 every time it fails
	factor = 2

	def buildProtocol(self,addr):
		print("Connecting to",addr)
		self.resetDelay()
		p = self.protocol()
		p.factory = self
		return p

	def clientConnectionFailed(self,conn,reason):
		super(Factory,self).clientConnectionFailed(conn,reason)
		print ("Failed to Connect")


if __name__ == "__main__":

	f = Factory()

	reactor.connectTCP("FamilyRoom",9090,f)
	reactor.run()

