#!/usr/bin/python

from gps import *

import time
import threading
import pickle

gpsd = None  # seting the global variable

class GPSPoller(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
        
            gpsd_data = {'latitude': gpsd.fix.latitude,
                         'longitude': gpsd.fix.latitude,
                         'timestamp': gpsd.fix.time,
                         'heading': gpsd.attitude.heading,
                         'speed': gpsd.fix.speed, 'roll': gpsd.attitude.roll,
                         'pitch': gpsd.attitude.pitch,
                         'yaw': gpsd.attitude.yaw}
            
            for key in gpsd_data:
                print('%s: %d' % key, gpsd_data[key])
            
            pickle.dump(gpsd_data, open("gpsd_data.p", "wb"))
            
            
            # continuously loop and grab each set of gpsd info to clear the buffer
            gpsd.next()
            time.sleep(0.5)

try:
    gpsd_thread = GPSPoller()
    gpsd_thread.start()
except NameError:
    print("GPS not configured properly on this device!")
    import sys
    sys.exit(1)