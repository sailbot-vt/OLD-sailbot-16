window.onload = function() {

	socket = new WebSocket('ws://127.0.0.1:8888/ws');

	socket.onmessage = function(s) {

		// parses the incoming socket message and gets the data from the message
		data = JSON.parse(s.data);

		if (data.category == "marker") {
			add_marker(data.type, data.location.latitude, data.location.longitude);
		}

		if (data.category == "log") {

			var type = get_log_type(data.type);
			var message;

			message = (data.message.indexOf("Data sent to the server") > -1) ? "Data sent to the server"
					: data.message;

			var console_message = document.getElementById('console').firstChild;

			if (console_message.innerHTML !== undefined) {
				var count = console_message.getElementsByTagName('var')[0];

				if (console_message.innerHTML.replace(
						/<([^>]+?)([^>]*?)>(.*?)<\/\1>/ig, "") == message) {
					if (isNaN(parseInt(count.innerHTML))) {
						count.innerHTML = 2;
					} else {
						count.innerHTML = parseInt(count.innerHTML) + 1;
					}

				} else {
					create_console_entry(type, message);
				}

			} else {
				create_console_entry(type, message);
			}

		}

		if (data.category == "data") {
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

function create_console_entry(type, message) {
	var div = document.createElement('div');

	div.innerHTML = '<span class="' + type + '"></span>' + message
			+ '<var></var>';

	document.getElementById('console').insertBefore(div,
			document.getElementById('console').firstChild);
}

function get_log_type(level) {
	switch (level) {
	case 10:
		return "debug";
	case 20:
		return "info";
	case 30:
		return "warning";
	case 40:
		return "error";
	case 50:
		return "critical";

	}
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