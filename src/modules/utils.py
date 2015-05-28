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

yellow = "\033[33m\033[1m"
green = "\033[32m\033[1m"
purple = "\033[35m\033[1m"
reset = "\033[0m\033[39m"

def print_terminal(data, values):
    print('\033c')
    print('%sTimestamp: %s' % (yellow, data['timestamp']))
    print('Location: %s%s' % (data['location'], reset))
    print('Heading: %0.5f' % data['heading'])
    print('Speed: %0.5f' % data['speed'])
    print('Wind Direction: %0.5f\n' % data['wind_dir'])
    print('Roll: %0.5f' % data['roll'])
    print('Pitch: %0.5f' % data['pitch'])
    print('Yaw: %0.5f\n' % data['yaw'])

    print('%sEvent: %s' % (green, values['event']))
    print('Debug: %r%s' % (values['debug'], reset))
    print('Web server port: %d\n' % values['port'])
    print('Transmission delay: %d' % values['transmission_delay'])
    print('Logic evaluation delay: %d\n' % values['eval_delay'])
    print('%sCurrent desired heading: %d' % (purple, values['current_desired_heading']))
    print('Direction: %d' % values['direction'])
    print('Absolute wind direction: %d%s\n' % (values['absolute_wind_direction'], reset))
    # print('Max turn rate angle: %d' % values['max_turn_rate_angle'])
    # print('Max rudder angle: %d' % values['max_rudder_angle'])
    # print('Max winch angle: %d\n' % values['max_winch_angle'])
    print('Preferred tack: %d' % values['preferred_tack'])
    print('Preferred gybe: %d\n' % values['preferred_gybe'])
    print('Winch angle: %d\n' % values['winch_angle'])
    print('Rudder angle: %d\n' % values['rudder_angle'])
    # print('Tack angle: %d' % values['tack_angle'])
    # print('Gybe angle: %d\n\n' % values['gybe_angle'])

    time.sleep(0.995)

def setup_config(values):

    # Logging in this method must stay as print statements because the logger
    # has not been defined yet

    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        values['debug'] = config.getboolean('DEFAULT', 'debug')
        values['port'] = float(config.getint('DEFAULT', 'port'))

        # Sets execution delays
        values['transmission_delay'] = float(config.get('DEFAULT', 'transmission_delay'))
        values['eval_delay'] = float(config.get('DEFAULT', 'eval_delay'))

        # Sets the tack and gybe angles
        values['gybe_angle'] = float(config.get('LOGIC', 'gybe_angle'))
        values['tack_angle'] = float(config.get('LOGIC', 'tack_angle'))

        # Sets the autonomous event
        values['event'] = config.get('DEFAULT', 'event')

        values['max_winch_angle'] = float(config.get('LOGIC', 'max_winch_angle'))
        values['max_rudder_angle'] = float(config.get('LOGIC', 'max_rudder_angle'))
        values['max_turn_rate_angle'] = float(config.get('LOGIC', 'max_turn_rate_angle'))

        modules.calc.point_proximity_radius = float(config.get('LOGIC', 'point_proximity_radius'))

        print('Configuration file successfully loaded.')

    except configparser.NoOptionError:
        print('The locations configuration file could not be found or is malformed!')

def setup_logging():

    log_format = '[%(asctime)s] %(threadName)-7s %(levelname)-0s: %(message)s'

    log_path = r'logs/' 
    if not os.path.exists(log_path): os.makedirs(log_path)

    logging.basicConfig(filename='logs/' + time.strftime("%Y-%m-%d %H-%M-%S") + '.log', format=log_format,
                        datefmt='%H:%M:%S', level=logging.DEBUG)

    # Add the console to the logging output
    root = logging.StreamHandler()
    root.setFormatter(logging.Formatter(log_format, '%H:%M:%S'))
    logging.getLogger().addHandler(root)

    logging.info('Log started on: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
