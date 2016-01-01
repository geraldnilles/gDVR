
dgram = require("dgram");

// Create a multi-cast listener socket
var client = dgram.createSocket('udp4');
client.bind(9090,function(){
	client.setBroadcast(true);

	msg="GDVR_KODI_DISCOVERY_REQUEST";
	client.send(msg,0,msg.length,9090,"192.168.0.255");

});

client.on("message",function(msg,rinfo){

	resp = msg.toString();
	console.log(resp);

	if (resp == "GDVR_KODI_DISCOVERY_RESPONSE"){
		console.log("KODI device found: %s",rinfo.address);
	}

});


