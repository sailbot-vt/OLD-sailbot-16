window.onload = function() {

	socket = new WebSocket('ws://127.0.0.1:8888/ws');

	socket.onmessage = function(s) {

		// parses the incoming socket message and gets the data from the message
		data = JSON.parse(s.data);

		if (data.category == "log") {
			var div = document.createElement('div');

			var type;

			switch (data.type) {
			case 10:
				type = "debug";
				break;
			case 20:
				type = "info";
				break;
			case 30:
				type = "warning";
				break;
			case 40:
				type = "error";
				break;
			case 50:
				type = "critical";
				break;

			}
			div.innerHTML = '<span class="' + type + '"></span>' + data.message;

			var t = document.getElementById('console');
			
			if (t.firstChild) {
				t.insertBefore(div, t.firstChild);
			}
			else {
				t.appendChild(div);
			}
		}

		if(data.category == "data") {
			document.getElementById("timestamp").innerHTML = data.timestamp;
			document.getElementById("lat").innerHTML = data.lat;
			document.getElementById("long").innerHTML = data.long;
			document.getElementById("target_lat").innerHTML = data.target_lat;
			document.getElementById("target_long").innerHTML = data.target_long;
			document.getElementById("heading").innerHTML = data.heading;
			document.getElementById("speed").innerHTML = data.speed;
			document.getElementById("wind_dir").innerHTML = data.wind_dir;
			document.getElementById("roll").innerHTML = data.roll;
			document.getElementById("pitch").innerHTML = data.pitch;
			document.getElementById("yaw").innerHTML = data.yaw;
			
			update_boat_marker(data.lat, data.long);
		}
	};

}

function set_console_height() {
	var h = document.getElementById("panel");
	var j = document.getElementById("console");

	document.getElementById("console").style.height = (document.body.scrollHeight - (h.clientHeight + 60))
			+ 'px';
	// there's 20px of padding around the panel div unaccounted for in addition
	// to the 20px padding offset
	// there's also a 20pc gap between the information above the console and the
	// console itself
}