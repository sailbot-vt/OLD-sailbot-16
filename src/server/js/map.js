function initialize() {
	var mapOptions = {
		center : {
			lat : 37.047764,
			lng : -79.639314
		},
		zoom : 14,
		disableDefaultUI : true,
		styles : [ {
			"featureType" : "water",
			"stylers" : [ {
				"color" : "#46bcec"
			}, {
				"visibility" : "on"
			} ]
		}, {
			"featureType" : "landscape",
			"stylers" : [ {
				"color" : "#f2f2f2"
			} ]
		}, {
			"featureType" : "road",
			"stylers" : [ {
				"saturation" : -100
			}, {
				"lightness" : 45
			} ]
		}, {
			"featureType" : "road.highway",
			"stylers" : [ {
				"visibility" : "simplified"
			} ]
		}, {
			"featureType" : "road.arterial",
			"elementType" : "labels.icon",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "administrative",
			"elementType" : "labels.text.fill",
			"stylers" : [ {
				"color" : "#444444"
			} ]
		}, {
			"featureType" : "transit",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "poi",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		} ]
	};

	var map = new google.maps.Map(document.getElementById('map-canvas'),
			mapOptions);

	var marker = new google.maps.Marker({
		position : {
			lat : 37.047764,
			lng : -79.639314
		},
		map : map,
		title : 'Hello World!'
	});

}
google.maps.event.addDomListener(window, 'load', initialize);
