#!/usr/bin/python
import time, threading, json, logging, tornado.websocket, modules.calc, math, modules.utils, modules.log, socket, sys
from modules.server import ServerThread
from modules.location import Location
from modules.calc import direction_to_point
from modules.control_thread import StoppableThread

# Variables and constants
data = {'category': 'data', 'timestamp': 0, 'location': Location(0, 0),
        'heading': 0, 'speed': 0, 'wind_dir': 0, 'roll': 0, 'pitch': 0,
        'yaw': 0}

target_locations = []
boundary_locations = []
location_pointer = 0

# Specifies the default values
values = {'event': 'default', 'debug': False, 'port': 80, 'transmission_delay': 5, 'eval_delay': 5, 'current_desired_heading': 0,
          'direction': 0, 'absolute_wind_direction': 0, 'max_turn_rate_angle': 70, 'max_rudder_angle': 40, 'max_winch_angle': 70,
          'tack_angle': 45, 'gybe_angle': 20, 'preferred_tack': 0, 'preferred_gybe': 0, 'winch_angle': 0, 'rudder_angle': 0}

## ----------------------------------------------------------
    
class DataThread(StoppableThread):

    """ Transmits the data object to the server thread
    """

    server_thread = None
    rudder_sock = None
    winch_sock = None

    def __init__(self, *args, **kwargs):
        super(DataThread, self).__init__(*args, **kwargs)

        global server_thread
        server_thread = ServerThread(name='Server', kwargs={'port': values['port'], 'target_locations': target_locations, 'boundary_locations': boundary_locations})
        server_thread.start()

        global rudder_sock
        try:
            rudder_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            rudder_sock.connect(("localhost", 9107))
        except socket.error:
            # Connection refused error
            logging.critical("Could not connect to servo socket")

        global winch_sock
        try:
            winch_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            winch_sock.connect(("localhost", 9108))
        except socket.error:
            # Connection refused error
            logging.critical("Could not connect to servo socket")


        # Set up logging to the web server console
        logging.getLogger().addHandler(modules.log.WebSocketLogger(self))

    def set_rudder_angle(self, angle):
        try:
            rudder_sock.send(str(angle).encode('utf-8'))
        except socket.error:
            # Broken Pipe Error
            logging.error('The rudder socket is broken!')

    def set_winch_angle(self, angle):
        try:
            winch_sock.send(str(angle).encode('utf-8'))
        except socket.error:
            # Broken Pipe Error
            logging.error('The winch socket is broken!')

    def send_data(self, data):

        # do not log any data here, doing so would create an infinite loop
        try:
            server_thread.send_data(data)
        except tornado.websocket.WebSocketClosedError:
            print('Could not send data because the socket is closed.')

    def run(self):
        
        logging.info('Starting the data thread!')
        
        # Connect to the GPS socket
        try:
            gps_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            gps_sock.connect(("localhost", 8907))
        except socket.error:
            # Connection refused error
            logging.critical("Could not connect to GPS socket")

        # Connect to the wind sensor socket
        try:
            wind_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            wind_sock.connect(("localhost", 8894))
        except socket.error:
            logging.critical("Could not connect to wind sensor socket")
        
        while True:

            if self.stopped():
                # Stop the server thread
                server_thread.stop()
                break
            
            # Query and update the GPS data
            try:
                gps_sock.send(str(0).encode('utf-8'))
                gps_parsed = json.loads(gps_sock.recv(128).decode('utf-8').strip('\x00'))

                # Update the data object
                data.update(gps_parsed)

                # Add the location as an embeded data structure
                data['location'] = Location(gps_parsed['latitude'], gps_parsed['longitude'])

                data['heading'] = 180
                
            except (AttributeError, ValueError, socket.error) as e:
                logging.error('The GPS socket is broken or sent malformed data!')
 
            # Query and update the wind sensor data
            try:
                wind_sock.send(str(0).encode('utf-8'))
                wind_parsed = json.loads(wind_sock.recv(1024).decode('utf-8'))
                data['wind_dir'] = wind_parsed
            except (ValueError, socket.error) as e:
                # Broken pipe error
                logging.error('The wind sensor socket is broken!')

            # Send data to the server
            server_thread.send_data(modules.utils.getJSON(data))
            logging.debug('Data sent to the server %s' % json.dumps(json.loads(modules.utils.getJSON(data))))

            # Wait in the loop
            time.sleep(values['transmission_delay'])


## ----------------------------------------------------------

class LogicThread(StoppableThread):
    
    def run(self):
        logging.info("Beginning autonomous navigation routines....")
        logging.warn("The angle is: %d" % data['wind_dir'])

        if (values['event'] == 'default'):
            logging.info("Starting the default event!")
            self.run_default()

        elif (values['event'] == 'station_keeping'):
            logging.info("Starting the station keeping event!")
            self.run_station_keeping()

    def station_keeping(self):
        while True:

            if self.stopped():
                break    
    
    def run_default(self):
        while True:

            if self.stopped():
                break

            # Update direction
            values['direction'] = modules.calc.direction_to_point(data['location'], target_locations[0])
            values['absolute_wind_direction'] = data['wind_dir'] + data['heading']
            
            time.sleep(values['eval_delay'])
            logging.debug("Heading: %d, Direction: %d, Wind: %d, Absolute Wind Direction: %d, Current Desired Heading: %d, Preferred Tack: %d, Preferred Gybe: %d" % (data['heading'], values['direction'], data['wind_dir'], values['absolute_wind_direction'], values['current_desired_heading'], values['preferred_tack'], values['preferred_gybe']))
            logging.debug("Upwind: %r, Downwind: %r" % (self.upwind(target_locations[location_pointer]), self.downwind(target_locations[location_pointer])))

            # If it's sailable, go straight to it
            if self.sailable(target_locations[location_pointer]):
                values['current_desired_heading'] = values['direction']
                values['preferred_tack'] = 0
                values['preferred_gybe'] = 0

            # It's not sailable; if it's upwind, tack
            elif self.upwind(target_locations[location_pointer]):
    
                if values['preferred_tack'] == 0:  # If the target's upwind and you haven't chosen a tack, choose one
                    values['preferred_tack'] = (180 - ((data['heading'] - values['absolute_wind_direction']) % 360)) / math.fabs(180 - ((data['heading'] - values['absolute_wind_direction']) % 360))
    
                if values['preferred_tack'] == -1:  # If the boat is on a left-of-wind tack
                    values['current_desired_heading'] = (values['absolute_wind_direction'] - values['tack_angle'] + 360) % 360
                    
                elif values['preferred_tack'] == 1: # If the boat is on a right-of-wind tack
                    values['current_desired_heading'] = (values['absolute_wind_direction'] + values['tack_angle'] + 360) % 360
                    
                else:
                    logging.error("The preferred tack was %d" % values['preferred_tack'])

            # Otherwise, gybe
            elif self.downwind(target_locations[location_pointer]):
    
                if values['preferred_gybe'] == 0:  # If the target's downwind and you haven't chosen a gybe, choose one
                    values['preferred_gybe'] = (180 - ((data['heading'] - values['absolute_wind_direction']) % 360)) / math.fabs(180 - ((data['heading'] - values['absolute_wind_direction']) % 360))
    
                if values['preferred_gybe'] == -1:  # If the boat is on a left-of-wind tack
                    values['current_desired_heading'] = (values['absolute_wind_direction'] + 180 + values['gybe_angle'] + 360) % 360
                    
                elif values['preferred_gybe'] == 1: # If the boat is on a right-of-wind tack
                    values['current_desired_heading'] = (values['absolute_wind_direction'] + 180 - values['gybe_angle'] + 360) % 360
                    
                else:
                    logging.error("The preferred gybe was %d" % values['preferred_gybe'])

            else:
                logging.critical('Critical logic error!')
                    
            self.turn_rudder()
            self.check_locations()
            logging.debug("Heading: %d, Direction: %d, Wind: %d, Absolute Wind Direction: %d, Current Desired Heading: %d, Sailable: %r\n" % (data['heading'], values['direction'], data['wind_dir'], values['absolute_wind_direction'], values['current_desired_heading'], self.sailable(target_locations[location_pointer])))

    # Checks to see if the target location is within a sailable region 
    def sailable(self, target_location):
        angle_of_target_off_the_wind = (values['direction'] - values['absolute_wind_direction'] + 360) % 360

        if angle_of_target_off_the_wind < values['tack_angle']:
            return False

        if angle_of_target_off_the_wind > (360 - values['tack_angle']):
            return False
        
        if (angle_of_target_off_the_wind > (180 - values['gybe_angle'])) and (angle_of_target_off_the_wind < (180 + values['gybe_angle'])):
            return False

        return True

    def upwind(self, target_location):
        angle_of_target_off_the_wind = (values['direction'] - values['absolute_wind_direction'] + 360) % 360
        return (angle_of_target_off_the_wind < values['tack_angle']) or (angle_of_target_off_the_wind > (360 - values['tack_angle']))

    def downwind(self, target_location):
        angle_of_target_off_the_wind = (values['direction'] - values['absolute_wind_direction'] + 360) % 360
        return (angle_of_target_off_the_wind > (180 - values['gybe_angle'])) and (angle_of_target_off_the_wind < (180 + values['gybe_angle']))

    def check_locations(self):
        global location_pointer
        logging.debug('Trying to sail to %s' % target_locations[location_pointer])

        if modules.calc.point_proximity(data['location'], target_locations[location_pointer]):
            logging.debug('Location %s has been reached! Now traveling to %s!' % (target_locations[location_pointer], target_locations[location_pointer + 1]))
            location_pointer += 1

    def turn_rudder(self):
        # Heading differential
        a = ((values['current_desired_heading'] - data['heading']) + 360) % 360
        if (a > 180):
            a -= 360

        # Cap the turn speed
        if (a > values['max_turn_rate_angle']):
            a = values['max_turn_rate_angle']

        # Cap the turn speed
        if (a < (-1 * values['max_turn_rate_angle'])):
            a = -1 * values['max_turn_rate_angle']

        values['rudder_angle'] = a * (values['max_rudder_angle'] / values['max_turn_rate_angle'])

        logging.debug('Set the rudder angle to: %f' % values['rudder_angle'])
        self._kwargs['data_thread'].set_rudder_angle(values['rudder_angle'])


    def turn_winch(self):
        a = data['wind_dir']

        if data['wind_dir'] > 180:
            a = 360 - a

        if a > (180 - values['gybe_angle']):
            a = 180 - values['gybe_angle']

        elif a < values['tack_angle']:
            a = values['tack_angle']

        a -= values['tack_angle']

        values['winch_angle'] = 80 - 40 * (a / (180 - values['gybe_angle'] - values['tack_angle']))

        logging.debug('Set the winch angle to: %f' % values['winch_angle'])
        self._kwargs['data_thread'].set_winch_angle(values['winch_angle'])

## ----------------------------------------------------------

def main():
    try:
        threading.current_thread().setName('Main')

        # Sets up the program configuration
        modules.utils.setup_config(values)
        if values['debug']:
            modules.utils.setup_logging()
            
        modules.utils.setup_locations(target_locations, boundary_locations)

        logging.info('Starting SailBOT!')

        data_thread = DataThread(name='Data')
        logic_thread = LogicThread(name='Logic', kwargs={'data_thread': data_thread})

        data_thread.start()
        logic_thread.start()

        time.sleep(5)

        while True:
            modules.utils.print_terminal(data, values)
            time.sleep(0.005)

    except KeyboardInterrupt:
        logging.critical('Program terminating!')
        # Stop the threads
        data_thread.stop()
        logic_thread.stop()

        # Join the threads into the main threads
        data_thread.join()
        logic_thread.join()

        # Terminate the program
        logging.critical('Program exited!')
        sys.exit()

if __name__ == '__main__':
    main()
            