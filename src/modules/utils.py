#!/usr/bin/python
import json, logging, configparser, modules.calc, time, os, sys, modules.log
import logging, curses, time
from datetime import datetime

logger = logging.getLogger('log')

def setup_logging():
    screen = curses.initscr()
    screen.nodelay(1)
    screen.border(0)

    maxy, maxx = screen.getmaxyx()

    height = 20
    # height, width, begin_y, begin_x
    win = curses.newwin(height, maxx-4, maxy-(height + 1), 2)


    curses.setsyx(-1, -1)
    screen.addstr(1,2, "SailBOT: the most advanced collegiate sailing operating system")
    screen.refresh()
    win.refresh()
    win.scrollok(True)
    win.idlok(True)
    win.leaveok(True)

    mh = modules.log.CursesHandler(win)
    formatterDisplay = logging.Formatter('[%(asctime)s] %(levelname)-0s: %(message)s', '%H:%M:%S')
    mh.setFormatter(formatterDisplay)
    logger.addHandler(mh)
    logger.setLevel(logging.DEBUG)

def shutdown_terminal():
    curses.curs_set(1)
    curses.nocbreak()
    curses.echo()
    curses.endwin()
   
def getJSON(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def setup_locations(target_locations, boundary_locations):
    try:
        with open('locations.json', 'r') as myfile:
            json_data = json.loads(myfile.read().replace('\n', ''))

        
        for location in json_data['target_locations']:
            target_locations.append({"latitude": location["latitude"], "longitude": location["longitude"]})
        for location in json_data['boundary_locations']:
            boundary_locations.append({"latitude": location["latitude"], "longitude": location["longitude"]})
            
        logger.info("Loaded the following target locations: %s" % target_locations)
        logger.info("Loaded the following boundary locations: %s" % boundary_locations)
        
    except IOError:
        logger.error('The locations JSON file could not be found!')
        sys.exit()
    except ValueError:
        logger.error('The locations JSON file is malformed!')
        sys.exit()

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

        values['station_keeping_timeout'] = float(config.get('DEFAULT', 'station_keeping_timeout'))

        modules.calc.point_proximity_radius = float(config.get('LOGIC', 'point_proximity_radius'))

        print('Configuration file successfully loaded.')

    except configparser.NoOptionError:
        print('The locations configuration file could not be found or is malformed!')

