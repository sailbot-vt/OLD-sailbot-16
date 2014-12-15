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

	overlay = new CustomMarker(map.getCenter(), map, 'boat');

}

function CustomMarker(latlng, map, type) {
	this.latlng_ = latlng;
	this.type = type;
	this.setMap(map);
}

CustomMarker.prototype = new google.maps.OverlayView();

CustomMarker.prototype.draw = function() {

	var div = this.div_;
	if (!div) {
		// create the overlay element
		div = this.div_ = document.createElement('DIV');
		div.style.border = "none";
		div.style.position = "absolute";
		div.style.paddingLeft = "0px";
		div.style.cursor = 'pointer';

		var d = document.createElement("div");

		d.className = (this.type == 'boat') ? 'pulse' : 'buoy';

		div.appendChild(d);

		// add the overlay to the DOM
		var panes = this.getPanes();
		panes.overlayImage.appendChild(div);
	}

	// position the overlay
	var point = this.getProjection().fromLatLngToDivPixel(this.latlng_);
	if (point) {
		div.style.left = point.x + 'px';
		div.style.top = point.y + 'px';
	}
};

google.maps.event.addDomListener(window, 'load', initialize);
