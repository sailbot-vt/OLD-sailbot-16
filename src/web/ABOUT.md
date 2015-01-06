#About Websocket Transmission

**Websocket Server ➜ Client Communication**

The navigation program also contains support for displaying dynamic a webpage, which will update with critical data pertaining to the state of the sail boat. It includes a map, a panel of variables, and a console of output.

The socket is defined in `websocket-client.js`:

    socket = new WebSocket('ws://127.0.0.1:80/ws');

When the [Raspberry Pi](http://www.raspberrypi.org/) setup is connected to a network, simply navigating to the IP of the device in a browser will render the page.

This side of the program is written entirely in native Javascript and CSS. No extra dependencies are required.

**Transmission Specifications**

All data sent to the client must contain the `category` tag. This is done so the client can sort the three types of messages it expects from the server:

 1. routine data messages: `category='data'`
 2. marker additions: `category='marker'`
 3. console logging messages: `category='log'`

**Data Request**

A sample JSON request contain a routine data message might look like this:

     {  
       "category":"data",
       "pitch":0,
       "target_lat":0,
       "state":0,
       "wind_dir":0,
       "target_long":0,
       "heading":0,
       "long":0,
       "timestamp":0,
       "lat":0,
       "speed":0,
       "yaw":0,
       "roll":0
    }


**Marker Request**

A sample JSON request containing marker definitions might look like this:

    {  
       "category":"marker",
       "type":"buoy",
       "location":{  
          "latitude":37.216769,
          "longitude":-80.005349
       }
    }


**Log Request**

A sample JSON request containing a log entry might look like this:

    {  
       "category":"log",
       "message":"200 GET / (::1) 12.73ms",
       "type":"20"
    }

