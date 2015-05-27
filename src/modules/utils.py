#!/usr/bin/python
import json, logging, configparser, modules.calc, time, os
from modules.location import Location
from datetime import datetime

def getJSON(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def location_decoder(obj):
    return Location(obj['latitude'], obj['longitude'])

def setup_locations(target_locations, boundary_locations):
    try:
        with open('locations.json', 'r') as myfile:
            json_data = json.loads(myfile.read().replace('\n', ''))

        i = []
        j = []
        
        for location in json_data['target_locations']:
            target_locations.append(location_decoder(location))
            i.append(location_decoder(location).__str__())
        for location in json_data['boundary_locations']:
            boundary_locations.append(location_decoder(location))
            j.append(location_decoder(location).__str__())
            
        logging.info("Loaded the following target locations: %s" % i)
        logging.info("Loaded the following boundary locations: %s" % j)
        
    except FileNotFoundError:
        logging.error('The locations JSON file could not be found!')
    except ValueError:
        logging.error('The locations JSON file is malformed!')

def setup_config(values):

    # Logging in this method must stay as print statements because the logger
    # has not been defined yet

    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        values['debug'] = config.getboolean('DEFAULT', 'debug')
        values['port'] = config.getint('DEFAULT', 'port')
        values['transmission_delay'] = config.get('DEFAULT', 'transmission_delay')
        values['eval_delay'] = config.get('DEFAULT', 'eval_delay')
        values['max_winch_angle'] = config.get('LOGIC', 'max_winch_angle')
        values['max_rudder_angle'] = config.get('LOGIC', 'max_rudder_angle')
        values['max_turn_rate_angle'] = config.get('LOGIC', 'max_turn_rate_angle')

        # Sets the autonomous event
        values['event'] = config.get('DEFAULT', 'event')

        modules.calc.point_proximity_radius = float(config.get('LOGIC', 'point_proximity_radius'))

        print('Configuration file successfully loaded.')

    except configparser.NoOptionError:
        print('The locations configuration file could not be found or is malformed!')

    if values['debug']:
        log_format = '[%(asctime)s] %(threadName)-7s %(levelname)-0s: %(message)s'

        log_path = r'logs/' 
        if not os.path.exists(log_path): os.makedirs(log_path)

        logging.basicConfig(filename='logs/' + time.strftime("%Y-%m-%d %H-%M-%S") + '.log', format=log_format,
                            datefmt='%H:%M:%S', level=logging.DEBUG)

        root = logging.StreamHandler()
        root.setFormatter(logging.Formatter(log_format, '%H:%M:%S'))

        logging.getLogger().addHandler(root)

        logging.info('Log started on: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
