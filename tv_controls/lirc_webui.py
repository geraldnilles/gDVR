#!/usr/bin/env python

from wsgiref.simple_server import make_server
import subprocess
import wsgiref.util


# In order to put everything in 1 file, i will dump the raw HTML here
MAIN_HTML = """<html>
<head>

<meta name="viewport" content = "width=device-width">
<meta name="viewport" content = "width=320">

<style>

body {
	width: 320px;
	font: 12pt Helvetica, sans-serif;
}


button{
	width: 300px ;
	height: 50px ;
}

div {
	margin-top: 10px;
}

</style>


<script>

function send_cmd(cmd){

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function(){
		if(xhttp.readyState == 4 && xhttp.status == 200) {
			document.getElementById("console").innerHTML = cmd+" Sent!";
		}
	}

	xhttp.open("GET",cmd,true);
	xhttp.send();
}


</script>

</head>
<body>

	<h2>TV Control</h2>

	<div><button onclick="send_cmd('power')">Power</button></div>
	<div><button onclick="send_cmd('sleep')">Sleep</button></div>
	<div><button onclick="send_cmd('volup')">Volume Up</button></div>
	<div><button onclick="send_cmd('voldown')">Volume Down</button></div>

	<div id="console"></div>

</body>
</html>
"""


def send_command(command):

	print("Sending",command)
	
	try:
		p = subprocess.Popen(["irsend",
			"-d","/run/lirc/lircd-lirc0", 
			"SEND_ONCE",
			"samsung",
			command])
		p.wait()
	except:
		pass




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
	elif "sleep" in path:
		return lirc(e,s,"BTN_SLEEP")
	elif "volup" in path:
		return lirc(e,s,"KEY_VOLUMEUP")
	elif "voldown" in path:
		return lirc(e,s,"KEY_VOLUMEDOWN")
	else:
		return main_html(e,s)


httpd = make_server('', 8080, lirc_app)
print ("Starting Server...")
httpd.serve_forever()

