

function bind(){
	var shows = document.getElementsByTagName("a");
	for (var i = 0; i < shows.length; i++){
		var s = shows[i];
		s.onclick=function(e){
			var name = e.target.innerHTML;
			debug("Play "+name);	
			play(name);
		}
	}
}

function play(show){
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange=function(){
		var state = xhttp.readyState;
		var sts = xhttp.sts;

		if(state == 4 && sts == 200){
			debug("Success! Set a playlist for "+show);	
		} else if(state == 4){
			debug("Something went wrong");
		} else {
			debug("Request processing..");
		}
	};	
	xhttp.open("GET","play?s="+show, true);
	xhttp.send();
}

function debug(msg){
	document.getElementById("debug").innerHTML = msg;
}

bind();
