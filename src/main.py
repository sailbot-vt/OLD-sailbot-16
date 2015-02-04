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
from pickle import FALSE
try:
    import modules.gps
except ImportError:
    pass
import modules.utils
import modules.logging

# Variables and constants

data = {'category': 'data', 'timestamp': 0, 'location': Location(0, 0),
        'heading': 0, 'speed': 0, 'wind_dir': 0, 'roll': 0, 'pitch': 0,
        'yaw': 0, 'state': 0}

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

    def send_data(self, data):

        # do not log any data here, doing so would create an infinite loop

        try:
            server_thread.send_data(data)
        except tornado.websocket.WebSocketClosedError:
            print('Could not send data because the socket is closed.')

    def run(self):
        global server_thread

        # set up logging
        logging.getLogger().addHandler(modules.logging.WebSocketLogger(self))
        
        logging.info('Starting the data thread!')
        
        # set up server
        server_thread = ServerThread(name='Server', kwargs={'port': values['port'], 'target_locations': target_locations, 'boundary_locations': boundary_locations})
        server_thread.start()
        
        # start logging GPS data
        try:
            gpsp = modules.gps.GPSPoller()
            gpsp.start()
        except NameError:
            logging.critical("GPS not configured properly!")
        
        while True:
            server_thread.send_data(modules.utils.getJSON(data))
            logging.debug('Data sent to the server %s'
                         % json.dumps(json.loads(modules.utils.getJSON(data))))
            time.sleep(float(values['transmission_delay']))


## ----------------------------------------------------------

class LogicThread(threading.Thread):

    preferred_tack = 0 # -1 means left tack and 1 means right tack; 0 not on a tack
    
    def run(self):
        logging.info('Beginning autonomous navigation routines....')
        
        while True:
            # update direction
            values['direction'] = modules.calc.direction_to_point(values['location'], target_locations[0])
            values['absolute_wind_direction'] = data['wind_dir'] + data['heading']
            
            time.sleep(values['eval_delay'])
            logging.debug("Heading: %d, Direction: %d, Wind: %d, Absolute Wind Direction: %d" % data['heading'], values['direction'], data['wind_dir'], values['absolute_wind_direction'])
            
            if self.sailable(target_locations[0]):
                current_desired_heading = values['direction']
                preferred_tack = 0
                
            else:
    
                if preferred_tack == 0:  # if the target is not sailable and you haven't chosen a tack, choose one
                    preferred_tack = (180 - data['heading']) / math.fabs(180 - data['heading'])
    
                if preferred_tack == -1:  # if the boat is on a left-of-wind tack
                    current_desired_heading = (data['heading'] - 45 + 360) % 360
                    
                elif preferred_tack == 1: # if the boat is on a right-of-wind tack
                    current_desired_heading = (data['heading']  + 45 + 360) % 360
                    
                else:
                    logging.error('The preferred_tack was %d' % preferred_tack)
                    
    def sailable(self, target_location):
        angle_of_target_off_the_wind = (values['direction'] - values['absolute_wind_direction'] + 360) % 360
        
        if(math.fabs(angle_of_target_off_the_wind) < 45):
            return False
        
        return True
        
    
                

## ----------------------------------------------------------

def turn_rutter_to(angle):
    pass

class MotorThread(threading.Thread):

    def set(self, property, value):
        try:
            f = open('/sys/class/rpi-pwm/pwm0/' + property, 'w')
            f.write(value)
            f.close()
        except:
            logging.error('Error writing to: ' + property + ' value: ' + value)

    def setServo(self, angle):
        self.set('servo', str(angle))

    def configureServos(self):
        self.set('delayed', '0')
        self.set('mode', 'servo')
        self.set('servo_max', '180')
        self.set('active', '1')

    def run(self):
        self.configureServos()


## ----------------------------------------------------------

if __name__ == '__main__':
    try:
        threading.current_thread().setName('Main')

        modules.utils.setup_config(values)
        modules.utils.setup_locations(target_locations, boundary_locations)

        logging.info('Starting SailBOT!')

        data_thread = DataThread(name='Data').start()
        motor_thread = MotorThread(name='Motor').start()
        time.sleep(10)
        logic_thread = LogicThread(name='Logic').start()

    except KeyboardInterrupt:
        logging.critical('Program terminating!')


            