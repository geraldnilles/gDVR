#!/usr/bin/env python

from wsgiref.simple_server import make_server
import subprocess
import wsgiref.util


# For testing, i will read it from the main html file
f = open("main.html")
MAIN_HTML = f.read()
f.close()

# In order to put everything in 1 file, i will dump the raw HTML here
#MAIN_HTML = """
#
#"""


def send_command(command):

	print("Sending",command)

	p = subprocess.Popen(["irsend",
			"-d","/run/lirc/lircd-lirc0", 
			"SEND_ONCE",
			"samsung",
			command])
	p.wait()




def lirc(e,s,command):
	status = '200 OK'
	headers = [('Content-type', 'text/plain')]
	s(status,headers)

	send_command(command)

	return ["LIRC %s Command"%command]


def main_html(e,s):
	
	status = '200 OK'
	headers = [('Content-type', 'text/html')]
	s(status,headers)
	
	return [MAIN_HTML]

def my404(e,s):
	status = '200 OK'
	headers = [('Content-type', 'text/plain')]
	s(status,headers)
	print "404"

	return ["Nope"]
	

def lirc_app(e, s):

	# Check Path
	path = wsgiref.util.request_uri(e)


	if path == "/":
		return main_html(e,s)
	elif "favicon" in path:
		return my404(e,s)
	elif "power" in path:
		return lirc(e,s,"BTN_POWER")
	elif "volup" in path:
		return lirc(e,s,"KEY_VOLUMEUP")
	elif "voldown" in path:
		return lirc(e,s,"KEY_VOLUMEDOWN")
	else:
		return main_html(e,s)


httpd = make_server('', 8080, lirc_app)
print ("Starting Server...")
httpd.serve_forever()

