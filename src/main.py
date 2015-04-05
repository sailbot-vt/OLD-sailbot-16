#!/usr/bin/python

import time
from modules.server import ServerThread
import threading
import json
from modules.location import Location
import logging
import tornado.websocket
import modules.calc
import math
from modules.calc import direction_to_point
import modules.utils
import modules.log
import socket
import sys
import socketserver

# Variables and constants

data = {'category': 'data', 'timestamp': 0, 'location': Location(0, 0),
        'heading': 0, 'speed': 0, 'wind_dir': 0, 'roll': 0, 'pitch': 0,
        'yaw': 0}

target_locations = []
boundary_locations = []

values = {'debug': False, 'port': 8888, 'log_name': 'sailbot.log',
          'transmission_delay': 5, 'eval_delay': 5, 'current_desired_heading': 0,
          'direction': 0, 'absolute_wind_direction': 0}



## ----------------------------------------------------------
    
class DataThread(threading.Thread):

    """ Transmits the data object to the server thread
    """

    server_thread = None

    def __init__(self, *args, **kwargs):
        super(DataThread, self).__init__(*args, **kwargs)

        global server_thread
        server_thread = ServerThread(name='Server', kwargs={'port': values['port'], 'target_locations': target_locations, 'boundary_locations': boundary_locations})
        server_thread.start()

        # set up logging
        logging.getLogger().addHandler(modules.log.WebSocketLogger(self))

    def send_data(self, data):

        # do not log any data here, doing so would create an infinite loop

        try:
            server_thread.send_data(data)
        except tornado.websocket.WebSocketClosedError:
            print('Could not send data because the socket is closed.')

    def run(self):
        
        logging.info('Starting the data thread!')
        
        
        # create the server processes 
        try:
            gps_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            gps_sock.connect(("localhost", 8907))
        except ConnectionRefusedError:
            logging.critical("Could not connect to GPS socket")

        try:
            wind_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            wind_sock.connect(("localhost", 8894))
        except ConnectionRefusedError:
            logging.critical("Could not connect to wind sensor socket")
        
        while True:
            
            # get and update the gps data
            try:
                gps_sock.send(str(0).encode('utf-8'))
                gps_parsed = json.loads(gps_sock.recv(1024).decode('utf-8'))
                data.update(gps_parsed)
                data.location = Location(gps_parsed.latitude, gps_parsed.longitude)
            except BrokenPipeError:
                logging.error('The GPS socket is broken!')

            # get and update the wind sensor data
            try:
                wind_sock.send(str(0).encode('utf-8'))
                wind_parsed = json.loads(wind_sock.recv(1024).decode('utf-8'))
                data.update(wind_parsed)
            except BrokenPipeError:
                logging.error('The wind sensor socket is broken!')

            # send data to the server
            server_thread.send_data(modules.utils.getJSON(data))
            logging.debug('Data sent to the server %s' % json.dumps(json.loads(modules.utils.getJSON(data))))

            # wait in the loop
            time.sleep(float(values['transmission_delay']))


## ----------------------------------------------------------
class LogicThread(threading.Thread):

    preferred_tack = 0 # -1 means left tack and 1 means right tack; 0 not on a tack
    
    def run(self):
        logging.info('Beginning autonomous navigation routines....')
        logging.warn('The angle is: %d' % data['wind_dir'])
        
        while True:
            # update direction
            values['direction'] = modules.calc.direction_to_point(data['location'], target_locations[0])
            values['absolute_wind_direction'] = data['wind_dir'] + data['heading']
            
            time.sleep(float(values['eval_delay']))
            logging.debug("Heading: %d, Direction: %d, Wind: %d, Absolute Wind Direction: %d" % (data['heading'], values['direction'], data['wind_dir'], values['absolute_wind_direction']))
            
            if self.sailable(target_locations[0]):
                current_desired_heading = values['direction']
                preferred_tack = 0
                
            else:
    
                if self.preferred_tack == 0:  # if the target is not sailable and you haven't chosen a tack, choose one
                    preferred_tack = (180 - data['heading']) / math.fabs(180 - data['heading'])
    
                if self.preferred_tack == -1:  # if the boat is on a left-of-wind tack
                    current_desired_heading = (data['heading'] - 45 + 360) % 360
                    
                elif self.preferred_tack == 1: # if the boat is on a right-of-wind tack
                    current_desired_heading = (data['heading']  + 45 + 360) % 360
                    
                else:
                    logging.error('The preferred_tack was %d' % preferred_tack)
                    
    def sailable(self, target_location):
        angle_of_target_off_the_wind = (values['direction'] - values['absolute_wind_direction'] + 360) % 360
        
        if(math.fabs(angle_of_target_off_the_wind) < 45):
            return False
        
        return True


## ----------------------------------------------------------

if __name__ == '__main__':
    try:
        threading.current_thread().setName('Main')

        modules.utils.setup_config(values)
        modules.utils.setup_locations(target_locations, boundary_locations)

        logging.info('Starting SailBOT!')

        data_thread = DataThread(name='Data').start()
        time.sleep(10)
        logic_thread = LogicThread(name='Logic').start()

    except KeyboardInterrupt:
        logging.critical('Program terminating!')


            