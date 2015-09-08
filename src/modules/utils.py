#!/usr/bin/python
try:
    import json, logging, configparser, modules.calc, time, os, sys, modules.log
    import logging, curses, time, socket
    from datetime import datetime
except:
    import os, time
    pass

logger = logging.getLogger('log')

def setup_logging(*positional_parameters, **keyword_parameters):
    logger.setLevel(logging.DEBUG)

    log_path = r'logs/' + time.strftime("%Y-%m-%d %H-%M-%S") + '/'
    if not os.path.exists(log_path): os.makedirs(log_path)

    if ('name' in keyword_parameters):
        file_handler = logging.FileHandler('logs/' + time.strftime("%Y-%m-%d %H-%M-%S") + '/' + keyword_parameters['name'] + '.log')
    else:
        file_handler = logging.FileHandler('logs/' + time.strftime("%Y-%m-%d %H-%M-%S") + '/' + "undefined" + '.log')

    file_handler.setLevel(logging.DEBUG)

    formatterDisplay = logging.Formatter('[%(asctime)s] %(levelname)-0s: %(message)s', '%H:%M:%S')
    file_handler.setFormatter(formatterDisplay)

    logger.addHandler(file_handler)

panel = None
def setup_terminal_logging():
    logger.setLevel(logging.DEBUG)
    global panel
    screen = curses.initscr()
    screen.nodelay(1)
    screen.border(0)

    maxy, maxx = screen.getmaxyx()

    height = 20
    # height, width, begin_y, begin_x
    window = curses.newwin(height, maxx-4, maxy-(height + 1), 2)

    panel = curses.newwin(25, maxx-4, 2, 2)
    panel.refresh()

    curses.setsyx(-1, -1)

    screen.refresh()
    window.refresh()
    window.scrollok(True)
    window.idlok(True)
    window.leaveok(True)

    terminal_handler = modules.log.CursesHandler(window)
    formatterDisplay = logging.Formatter('[%(asctime)s] %(levelname)-0s: %(message)s', '%H:%M:%S')
    terminal_handler.setFormatter(formatterDisplay)
    logger.addHandler(terminal_handler)

def update_terminal_display(data, values):
    global panel

    panel.addstr(0, 0, "SailBOT Terminal Display", curses.A_BOLD)
    panel.addstr(2, 0, "location: " + str(data['location']))
    panel.refresh()

    for k, j in enumerate([data, values]):
        for index, (key, value) in enumerate(j.items()):
            if "location" in key:
                continue
            panel.addstr(index + 4, k * 45, str(key) + ": " + str(value))
            panel.refresh()

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


from enum import Enum
class SocketType(Enum):
    arduino = 7893
    rudder = 9107
    winch = 9108
    gps = 8907
    wind = 8894

def socket_connect(type):
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect(("localhost", type.value))
    except socket.error:
        logger.error("Could not connect to %s socket" % type.name)
        pass
    finally:
        return connection
