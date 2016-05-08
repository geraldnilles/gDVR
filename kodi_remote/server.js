
dgram = require("dgram");
fs = require("fs");
path = require("path");
http = require("http");
exec = require("child_process").exec;
url = require("url");
qs = require("querystring");

var kodis = ["BedroomRPi"];


// List of episodes which have been watched
watched = [];

// Assume the TV is off when the server is started
var tvIsOn = false;
var unixSocketPath = "/tmp/kodi.socket"


// Discovery Kodi Addresses
//
// Performs a UDP broadcast to search for kodi instances running on the local
// network.
function discover_kodi_addrs(){

	// Send a discovery message to all devices on the local network 
	var client = dgram.createSocket('udp4');
	client.bind(9090,function(){
		client.setBroadcast(true);

		var msg="GDVR_KODI_DISCOVERY_REQUEST";
		client.send(msg,0,msg.length,9090,"192.168.0.255");

		// Close this socket 1s after the requesting 

	});

	// Receive responses from discovery message
	client.on("message",function(msg,rinfo){

		var resp = msg.toString();
		console.log(resp);

		if (resp == "GDVR_KODI_DISCOVERY_RESPONSE"){
			console.log("KODI device found: %s",rinfo.address);
			kodi_addrs.push(rinfo.address);
		}

	});
}


// Update the kodi status
// 
// CHecks the status of the kodi instance.  This function should be run
// periodically (once a minute).  It will keep the server-side database in sync
// with the actual kodi.  It will also keep the TV's power state in sync.
// Eventually when i get JSON notifications working, this can be done
// asyncronously without polling.
function update_status(kodi){
	// CHeck if there is an active player
	get_playerids(null,function(pids){
		// If there are PIDs, a player is active
		if(pids.length > 0){
			if(!tvIsOn){
				// TV off but video is playing, turn on TV
				power(null);
				tvIsOn = true;
			}
		// If there are no PIDs, there are no shows playing
		}else{
			if(tvIsOn){
				// TV is on but video is done, Turn off TV
				power(null);
				tvIsOn = false;
			}		
		}
	});
}

// Kodi Message Request
//
// This function will send HTTP commands to a kodi device.  for now, is
// hardwired to BedroomRPi, but it will eventaully be configurable to any IP
// address.
function kodi_request(msg,callback){
	console.log(JSON.stringify(msg));

	var options = {
		hostname: "BedroomRPi",
		port: 80,
		path: "/jsonrpc?request="+qs.escape(JSON.stringify(msg)),
		method: "GET",
		headers:{
			'Content-Type': 'application/json'
		}
	}
	var req = http.request(options,function(res){
		res.setEncoding('utf8');
		res.on('data',function(chunk){
			console.log(chunk);
			callback(JSON.parse(chunk));
		});
	
	});

	req.on('error',function(e){
		console.log("Error Talking to Kodi", options["hostname"],
				e.message);
	});

	req.setTimeout(20000,function(e){
		console.log("Request Timeout");
	});

	req.end();

}

// Clear Kodi's playlist
function clear_playlist(kodi,callback){
	get_playlistid(kodi,function(pid){
		//Msg
		var msg = {
			jsonrpc: "2.0",
			id: 1,
			//method: "Playlist.GetItems",
			method: "Playlist.Clear",
			params: {
				playlistid:pid
			}
		}

		

		kodi_request(msg,function(resp){
			callback();
		});


	});
}

// Clear Kodi's playlist
function list_playlist(kodi,callback){
	get_playlistid(kodi,function(pid){
		//Msg
		var msg = {
			jsonrpc: "2.0",
			id: 1,
			method: "Playlist.GetItems",
			//method: "Playlist.Clear",
			params: {
				playlistid:pid
			}
		}

		

		kodi_request(msg,function(resp){
			callback();
		});


	});
}

function get_playlistid(kodi,callback){
	var msg = {
		jsonrpc: "2.0",
		id: 1,
		method: "Playlist.GetPlaylists"
	}
	kodi_request(msg,function(resp){
		var playlists = resp["result"];
		var pid = 0;
		for(var i = 0; i<playlists.length; i++){
			if(playlists[i]["type"] == "video"){
				pid = playlists[i]["playlistid"];
			}
		}
		callback(pid);
	});
}

// Add Items to Playlist
//
// This function adds items to a playlist.  This function is asyncronous and
// uses recursion to load the entire list of paths 1 by 1.
//
// @param - kodi - A dictionary object containing info about the kodi client
// @param - paths - A list of strings that describe the file paths
// @param - pid - the playlist ID you are adding to.  If null, the pid will be
// 	    automatically detected
// @param - callback - a function to run after the entire playlist is loaded
function add_to_playlist(kodi,paths,pid,callback){

	// If no PID was given, figure it out by asking kodi client and then
	// Recall the same function with the PID provided
	if(pid == null){

		get_playlistid(kodi,function(pid){
			add_to_playlist(kodi,paths,pid,callback);
		});
	} else {
		// End of Recursion.  No more items to add to playlist
		if(paths.length == 0){
			// Return
			callback();
			return;
		}

		// Remove the first item from the array
		var item = paths.shift();
		//Msg
		var msg = {
			jsonrpc: "2.0",
			id: 1,
			method: "Playlist.Add",
			params: {
				playlistid:pid,
				item: {file:item}
			}
		}
		// Call the same function again with the reduced arr
		kodi_request(msg,function(resp){
			add_to_playlist(kodi,paths,pid,callback);
		});


	}
}

function play(kodi,pid,callback){
	if(pid == null){
		get_playlistid(kodi,function(pid){
			play(kodi,pid,callback);
		});
	} else {
		
		var msg = {
				jsonrpc: "2.0",
				id: 1,
				method: "Player.Open",
				params: {
					item: {
						playlistid:pid
					}
				}
		}

		kodi_request(msg,function(resp){
			callback();
		});	
	}
}

function get_playerids(kodi,callback){
	var msg = {
		jsonrpc: "2.0",
		id: 1,
		method: "Player.GetActivePlayers"
	}
	kodi_request(msg,function(resp){
		var players = resp["result"];
		callback(players);
	});
}

function stop(kodi,pids,callback){
	if(pids == null){
		get_playerids(kodi,function(p){
			stop(kodi,p,callback);
		});
	}else{
		if(pids.length == 0){
			callback();
			return;
		}

		var item = pids.shift();
		var msg = {
			jsonrpc: "2.0",
			id: 1,
			method: "Player.Stop",
			params: {
				playerid:item["playerid"]
			}
		}
		kodi_request(msg,function(resp){
			stop(kodi,pids,callback);
		});
	}	
}

function display_status(kodi){

}

function vol_up(kodi){
	lirc_send(kodi,"KEY_VOLUMEUP");
}

function vol_down(kodi) {
	lirc_send(kodi,"KEY_VOLUMEDOWN");
}

function power(kodi){
	lirc_send(kodi,"BTN_POWER");
	console.log("Toggling TV Power");
}

function lirc_send(kodi,command){
	// Use SSH to send and LIRC command on the kodi box
	exec("ssh root@BedroomRPi"
		+" \"irsend -d /run/lirc/lircd-lirc0 SEND_ONCE samsung "
		+command+"\"",function(err,stdout,stderr){
		// Check output and make sure everything went well
		if(stdout.length > 0 || stderr.length > 0){
			console.log(stdout);
			console.log(stderr);
		}
	});
}



// Return a list of TV shows that match the query string
function findShows(query,callback){
	var tvPath = "/src/nfs4/media/TV";

	fs.readdir(tvPath,function(err,files){
		var out = [];
		for (var i = 0; i<files.length; i++){
			// Skip hidden folders
			if(files[i][0] == "."){
				continue
			}
			out.push(path.join(tvPath,files[i]))
		}
		callback(out);
	});
}

// Generate Random Playlist
function generatePlaylist(showPath,numOfEpisodes,callback){
	fs.readdir(showPath,function(err,files){
		// Figure out the maximum starting point of the playlist
		var max = files.length-numOfEpisodes;
		// If less than 0, play every episode
		if(max <= 0){
			var i = 0;
			var end = files.length;
		// Otherwise, find a randome starting point
		} else {
			var i = Math.floor(Math.random()*max);
			var end = i+numOfEpisodes;
		}

		var out = [];
		for (; i < end; i++){
			if(files[i][0] == "."){
				continue
			}
			out.push("nfs://server"+path.join(showPath,files[i]))
		}	
		callback(out);
	});
}

// Test Secion
// Clear the playlist and add 3 episodes to the Queue

function play_show(show,num){

	stop(null,null,function(){
		clear_playlist(null,function(){
			generatePlaylist("/srv/nfs4/media/TV/"+show,num,function(paths){
				add_to_playlist(null,paths,null,function(){
					list_playlist(null,function(){
						play(null,null,function(){
							update_status(null);
						});
					});
				});
			});
		});
	});
}

function fileHandler(name,req,resp){
	fs.readFile(name,"utf8",function(err,data){
		if(name.search("html")>0){
			resp.writeHead(200, {"Content-Type":"text/html"});
		}else{
			resp.writeHead(200, {"Content-Type":"text/plain"});
		}
		resp.write(data);
		resp.end();
	});
}

function playHandler(req,resp){
	var show = url.parse(req.url,true)["query"]["s"];	
	console.log("Play! ",show);
	resp.writeHead(200,{"Content-Type":"text/plain"});
	play_show(show,5);
	resp.write("OK");
	resp.end();
}

function commandHandler(req,resp){
	var command = url.parse(req.url,true)["query"]["c"];
	console.log("Command! ",command);
	resp.writeHead(200,{"Content-Type":"text/plain"});
	if(command == "Stop"){
		stop(null,null,function(){});
	}else if(command == "Volume Up"){
		vol_up(null);
	}else if(command == "Volume Down"){
		vol_down(null);
	}else{
		console.log("Unknown Command");
	}
	resp.write("OK");
	resp.end();
}

function httpHandler(req,resp){
	if (req.url.search("play") > 0) {
		playHandler(req,resp);
	} else if (req.url.search("command") > 0) {
		commandHandler(req,resp);
	}else if (req.url.search("frontend.js") > 0) {
		fileHandler("frontend.js",req,resp);
	}else if (req.url.search("html") > 0){
		fileHandler("frontend.html",req,resp);
	}else{
		resp.writeHead(404,{"Content-Type":"text/plain"});
		resp.end();
	}
}

function setup_server(){
	var server = http.createServer(httpHandler);

	if(fs.existsSync(unixSocketPath)){
		fs.unlink(unixSocketPath);
	}

	server.listen(unixSocketPath);

	fs.chmodSync(unixSocketPath,"777");
	console.log("Server Started");
}

setup_server();
// Setup Kodi Update Heartbeat Check
setInterval(update_status,30000,null);


// vim:tw=80
