window.onload = function() {

	socket = new WebSocket('ws://127.0.01:4041/ws');
	
	socket.onmessage = function(s) {
		alert('Received: ' + s);
	};

}