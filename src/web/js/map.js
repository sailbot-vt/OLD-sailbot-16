var marker;

function initialize() {
	var mapOptions = {
		center : {
			lat : 37.047764,
			lng : -79.639314
		},
		zoom : 14,

		panControl : true,
		zoomControl : true,
		mapTypeControl : false,
		scaleControl : true,
		streetViewControl : false,
		overviewMapControl : false,

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

	marker = new CustomMarker({
        position: map.getCenter(),
        map: map,
        content: '<div class="pulse"></div>',
    });

	var location = new google.maps.LatLng(37.046764, -79.637314)
	
	marker.setPosition(location);

}

google.maps.event.addDomListener(window, 'load', initialize);

function update_boat_marker(lat, long)
{
	var location = new google.maps.LatLng(lat, long)
	marker.setPosition(location);
}
