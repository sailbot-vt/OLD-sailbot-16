import json
import modules.calc
from modules.location import Location
import logging
import configparser
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

    # logging in this method must stay as print statements because the logger
    # has not been defined yet

    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        values['debug'] = config.getboolean('DEFAULT', 'debug')
        values['port'] = config.getint('DEFAULT', 'port')
        values['log_name'] = config.get('DEFAULT', 'log_name')
        values['transmission_delay'] = config.get('DEFAULT', 'transmission_delay')
        values['eval_delay'] = config.get('DEFAULT', 'eval_delay')

        modules.calc.point_proximity_radius = config.get('LOGIC',
                'point_proximity_radius')

        print('Configuration file successfully loaded.')
    except configparser.NoOptionError:
        print('The locations configuration file could not be found or is malformed!')

    if values['debug']:
        log_format = \
            '[%(asctime)s] %(threadName)-7s %(levelname)-0s: %(message)s'

        logging.basicConfig(filename=values['log_name'], format=log_format,
                            datefmt='%H:%M:%S', level=logging.DEBUG)

        root = logging.StreamHandler()
        root.setFormatter(logging.Formatter(log_format, '%H:%M:%S'))

        logging.getLogger().addHandler(root)

        logging.info('-------------------------------')
        logging.info('Log started on: %s'
                     % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
