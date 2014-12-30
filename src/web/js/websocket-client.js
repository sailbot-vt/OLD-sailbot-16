window.onload = function() {

	socket = new WebSocket('ws://127.0.0.1:8888/ws');

	socket.onmessage = function(s) {
		
		// parses the incoming socket message and gets the data from the message
		data = JSON.parse(s.data);
		
		if (data.hasOwnProperty('message')) {
			var div = document.createElement('div');
			
			var type;
			
			switch(data.type) {
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
			div.innerHTML = '<span class="'+ type + '"></span>' + data.message;
			
			document.getElementById('console').appendChild(div);
		}
		
		if (data.hasOwnProperty('timestamp')) {
		    document.getElementById("timestamp").innerHTML = data.timestamp;
		}

		if (data.hasOwnProperty('lat')) {
		    document.getElementById("lat").innerHTML = data.lat;
		}
		if (data.hasOwnProperty('long')) {
		    document.getElementById("long").innerHTML = data.long;
		}

		if (data.hasOwnProperty('target_lat')) {
		    document.getElementById("target_lat").innerHTML = data.target_lat;
		}

		if (data.hasOwnProperty('target_long')) {
		    document.getElementById("target_long").innerHTML = data.target_long;
		}

		if (data.hasOwnProperty('heading')) {
		    document.getElementById("heading").innerHTML = data.heading;
		}

		if (data.hasOwnProperty('speed')) {
		    document.getElementById("speed").innerHTML = data.speed;
		}
		if (data.hasOwnProperty('wind_dir')) {
		    document.getElementById("wind_dir").innerHTML = data.wind_dir;
		}
		if (data.hasOwnProperty('roll')) {
		    document.getElementById("roll").innerHTML = data.roll;
		}
		if (data.hasOwnProperty('pitch')) {
		    document.getElementById("pitch").innerHTML = data.pitch;
		}
		if (data.hasOwnProperty('yaw')) {
		    document.getElementById("yaw").innerHTML = data.yaw;
		}

		if ((data.hasOwnProperty('lat')) && (data.hasOwnProperty('long'))) {
		    update_boat_marker(data.lat, data.long);
		}

	};

}