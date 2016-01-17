
dgram = require("dgram");
fs = require("fs");
path = require("path");
http = require("http");

kodi_addrs = [];

// List of episodes which have been watched
watched = [];

function discover_kodi_addrs(){

	// Send a discovery message to all devices on the local network 
	var client = dgram.createSocket('udp4');
	client.bind(9090,function(){
		client.setBroadcast(true);

		msg="GDVR_KODI_DISCOVERY_REQUEST";
		client.send(msg,0,msg.length,9090,"192.168.0.255");

		// Close this socket 1s after the requesting 

	});

	// Receive responses from discovery message
	client.on("message",function(msg,rinfo){

		resp = msg.toString();
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
	// Talk to Kodi's address and check it's status
	// if Kodi's TV is on and playback is stopped, turn the TV off
	// If Kodi's TV is off and playback is going on, turn the TV On
}

function kodi_request(msg,callback){
	console.log(JSON.stringify(msg));

	var options = {
		hostname: "BedroomRPi",
		port: 80,
		path: "/jsonrpc?request="+JSON.stringify(msg),
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

	req.end();

}

// Clear Kodi's playlist
function clear_playlist(kodi){
	get_playlistid(kodi,function(pid){
		//Msg
		msg = {
			jsonrpc: "2.0",
			id: 1,
			method: "Playlist.GetItems",
			//method: "Playlist.Clear",
			params: {
				playlistid:pid
			}
		}

		

		kodi_request(msg,function(resp){
			;
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
		console.log("PID Found: "+pid);
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
			add_to_playlist(kodi,paths,pid);
		});
	} else {
		if(paths.length == 0){
			// Return
			callback();
		}

		// Remove the first item from the array
		var item = paths.shift()
		//Msg
		msg = {
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
			add_to_playlist(kodi,paths,pid);
		});


	});
}

function play(kodi,callback){

}

function stop(kodi,callback){

}

function display_status(kodi){

}

function vol_up(kodi){
	lirc_send(kodi,"KEY_VOLUP");
}

function vol_dow(kodi) {
	lirc_send(kodi,"KEY_VOLDOWN");
}

function power(kodi){
	lirc_send(kodi,"BTN_PWR");
}

function lirc_send(kodi,command){
	// Use SSH to send and LIRC command on the kodi box
	exec("ssh root@"+kodi.address+" irsend -d /run/lirc/lircd-lirc0 SEND_ONCE samsung "+command,function(){
		// Check output and make sure everything went well
	});
}



// Return a list of TV shows that match the query string
function findShows(query,callback){
	var tvPath = "/mnt/raid/TV";

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
		var max = files.length-numOfEpisodes;
		if(max <= 0){
			var i = 0;
			var end = files.length;
		} else {
			var i = Math.floor(Math.random()*max);
			var end = i+numOfEpisodes;
		}

		console.log(i,end);

		var out = [];
		for (; i < end; i++){
			if(files[i][0] == "."){
				continue
			}
			out.push(path.join(showPath,files[i]))
		}	
		callback(out);
	});
}

// Test Secion
add_to_playlist(1,1)
clear_playlist(0)


// vim:tw=80
