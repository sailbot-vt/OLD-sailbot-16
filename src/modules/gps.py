#!/usr/bin/python

import os
import logging
try:
    from gps import *
except ImportError:
    pass
from time import *
import time
import threading

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
            gpsd.next()  # continuously loop and grab each set of gpsd info to clear the buffer


            