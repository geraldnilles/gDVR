
var http = require('http');
var fs = require('fs');

var unixSocketPath = "/tmp/app.socket";

function pathHandler(req,resp){
	if (req.url.search("movie") > 0 ){
		movieHandler(req,resp);
	} else if (req.url.search("raid") > 0 ){
		raidHandler(req,resp);
	} else {
		resp.writeHead(404,{"Content-Type":"text/plain"});
		resp.end();
	}
	console.log(req.url);
}

// This presents a list of movies on the server
function movieHandler(req,resp){
	resp.writeHead(200, {"Content-Type":"text/plain"});
	resp.end("Movie List\n");	
}

// This tells whether or not he Raid is OK
function raidHandler(req,resp){
	resp.writeHead(200, {"Content-Type":"text/plain"});
	fs.readFile("/proc/mdstat","utf8",function(err,data){
		resp.write(data);
		if(data.search("\[U+\]") > 0){
			resp.end("\n\nOK");
		} else {
			resp.end("\n\nBAD");
		}
	});
	resp.write("Raid Status: \n");	
}

var server = http.createServer(pathHandler);


if(fs.existsSync(unixSocketPath)){
	fs.unlinkSync(unixSocketPath);
}

server.listen(unixSocketPath);

fs.chmodSync(unixSocketPath,"777");

console.log("Server Started");

// vim:tw=80
