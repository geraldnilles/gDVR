
dgram = require("dgram");

// Create a multi-cast listener socket
var s = dgram.createSocket('udp4');
s.bind(9090,function(){
	s.addMembership('224.0.0.114');
});

// When a new message is received...
s.on('message',function(msg,rinfo){

	var req = msg.toString();
	console.log("Message",req);

	// After getting a message, verify it is valid request and send back a
	// response
	if (req == "GDVR_KODI_DISCOVERY_REQUEST"){ 
		var resp="GDVR_KODI_DISCOVERY_RESPONSE";
		s.send(resp,0,resp.length,rinfo.port,rinfo.address); 
	}

});



