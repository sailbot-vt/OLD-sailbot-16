#!/usr/bin/python

import time
from modules.server import ServerThread
from modules.data import Data
import threading
import json
from modules.location import Location
import configparser
import logging
from datetime import datetime
import tornado.websocket

# Variables and constants

data = Data(
    timestamp=0,
    lat=0,
    long=0,
    target_lat=0,
    target_long=0,
    heading=0,
    speed=0,
    wind_dir=0,
    roll=0,
    pitch=0,
    yaw=0,
    state=0,
    )
servos = Data(rutter=0, sail=0)
locations = []

DEBUG = False
PORT = 8888
LOG_NAME = 'sailbot.log'


def location_decoder(obj):
    return Location(obj['latitude'], obj['longitude'])


def get_locations():
    try:
        with open('locations.json', 'r') as myfile:
            json_data = myfile.read().replace('\n', '')
        locations = json.loads(json_data, object_hook=location_decoder)

        logging.info('Loaded the following locations:')
        for location in locations:
            logging.info(location.__str__())
    except FileNotFoundError:

        logging.error('The locations JSON file could not be found!')
    except ValueError:
        logging.error('The locations JSON file is malformed!')


def get_config():
    global DEBUG
    global PORT
    global LOG_NAME

    # logging in this method must stay as print statements because the logger
    # has not been defined yet
    
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        DEBUG = config.getboolean('DEFAULT', 'debug')
        PORT = config.getint('DEFAULT', 'port')
        LOG_NAME = config.get('DEFAULT', 'log_name')

        print('Configuration file successfully loaded.')
    except configparser.NoOptionError:

        print('The locations configuration file could not be found or is malformed!')

class WebSocketLogger(logging.StreamHandler):
    """
    A handler class which allows the cursor to stay on
    one line for selected messages
    """
    def emit(self, record):
        try:
            packet = Data(message=self.format(record), type=record.levelno)
            data_thread.send_data(packet.to_JSON())
            self.flush()
        except NameError:
            print("The server thread has not been created yet. Dropping log output.")
        except:
            self.handleError(record)
            
            
def setup_config():
    if DEBUG:
        LOG_FORMAT = "[%(asctime)s] %(threadName)-7s %(levelname)-0s: %(message)s"
        
        logging.basicConfig(filename=LOG_NAME, format=LOG_FORMAT, datefmt='%H:%M:%S', level=logging.DEBUG)
 
        root = logging.StreamHandler()
        root.setFormatter(logging.Formatter(LOG_FORMAT, "%H:%M:%S"))
        
        logging.getLogger().addHandler(root)
        logging.getLogger().addHandler(WebSocketLogger())
        
        logging.info('-------------------------------')
        logging.info('Log started on: %s'
                     % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


## ----------------------------------------------------------

class DataThread(threading.Thread):

    """ Transmits the data object to the server thread
    """
    server_thread = None;
    
    def send_data(self, data):
        try:
            server_thread.send_data(data)
        except tornado.websocket.WebSocketClosedError:
            logging.error("Could not send data because the socket is closed.")

    def run(self):
        global server_thread
        
        logging.info('Starting the data thread!')
        DELAY_PERIOD = 5  # time between transmission in seconds
        server_thread = ServerThread(name="Server", kwargs={'PORT': PORT})
        server_thread.start()

        while True:
            server_thread.send_data(data.to_JSON())
            logging.info('Data sent to the server %s' % json.dumps(json.loads(data.to_JSON())))
            time.sleep(DELAY_PERIOD)


## ----------------------------------------------------------

class LogicThread(threading.Thread):

    def run(self):
        pass


## ----------------------------------------------------------

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
threading.current_thread().setName('Main')

get_config()
setup_config()
get_locations()

logging.info('Beginning SailBOT autonomous navigation routines....')

data_thread = DataThread(name="Data")
motor_thread = MotorThread(name="Motor")
logic_thread = LogicThread(name="Logic")

data_thread.start()
motor_thread.start()
logic_thread.start()

