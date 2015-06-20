
import socket, logging, json, time

from .log import WebSocketLogger
from .utils import getJSON
from .control_thread import StoppableThread
from .server import ServerThread

logger = logging.getLogger('log')

class DataThread(StoppableThread):

    server_thread = None
    rudder_sock = None
    winch_sock = None

    def __init__(self, *args, **kwargs):
        super(DataThread, self).__init__(*args, **kwargs)

        global server_thread
        server_thread = ServerThread(name='Server', kwargs={'port': self._kwargs['values']['port'], 'target_locations': self._kwargs['values']['target_locations'], 'boundary_locations': self._kwargs['values']['boundary_locations']})
        server_thread.start()

        global rudder_sock
        try:
            rudder_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            rudder_sock.connect(("localhost", 9107))
        except socket.error:
            # Connection refused error
            logger.critical("Could not connect to servo socket")

        global winch_sock
        try:
            winch_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            winch_sock.connect(("localhost", 9108))
        except socket.error:
            # Connection refused error
            logger.critical("Could not connect to servo socket")


        # Set up logging to the web server console
        # logging.getLogger('log').addHandler(WebSocketLogger(self))

    def set_rudder_angle(self, angle):
        try:
            rudder_sock.send(str(angle).encode('utf-8'))
        except socket.error:
            # Broken Pipe Error
            logger.error('The rudder socket is broken!')

    def set_winch_angle(self, angle):
        try:
            winch_sock.send(str(angle).encode('utf-8'))
        except socket.error:
            # Broken Pipe Error
            logger.error('The winch socket is broken!')

    def send_data(self, data):

        # do not log any data here, doing so would create an infinite loop
        try:
            server_thread.send_data(self._kwargs['data'])
        except tornado.websocket.WebSocketClosedError:
            print('Could not send data because the socket is closed.')

    def run(self):
        
        logger.info('Starting the data thread!')
        
        # Connect to the GPS socket
        try:
            gps_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            gps_sock.connect(("localhost", 8907))
        except socket.error:
            # Connection refused error
            logger.critical("Could not connect to GPS socket")

        # Connect to the wind sensor socket
        try:
            wind_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            wind_sock.connect(("localhost", 8894))
        except socket.error:
            logger.critical("Could not connect to wind sensor socket")
        
        while True:

            if self.stopped():
                # Stop the server thread
                server_thread.stop()
                break
            
            # Query and update the GPS data
            try:
                gps_sock.send(str(0).encode('utf-8'))
                gps_parsed = json.loads(gps_sock.recv(256).decode('utf-8').strip('\x00'))

                # Update the data object
                self._kwargs['data'].update(gps_parsed)

                # Add the location as an embeded data structure
                self._kwargs['data']['location'] = Location(gps_parsed['latitude'], gps_parsed['longitude'])
                
            except (AttributeError, ValueError, socket.error) as e:
                logger.error('The GPS socket is broken or sent malformed data!')
 
            # Query and update the wind sensor data
            try:
                wind_sock.send(str(0).encode('utf-8'))
                wind_parsed = json.loads(wind_sock.recv(1024).decode('utf-8'))
                self._kwargs['data']['wind_dir'] = wind_parsed
            except (ValueError, socket.error) as e:
                # Broken pipe error
                logger.error('The wind sensor socket is broken!')

            # Send data to the server
            server_thread.send_data(getJSON(self._kwargs['data']))
            logger.debug('Data sent to the server %s' % json.dumps(json.loads(getJSON(self._kwargs['data']))))

            # Wait in the loop
            time.sleep(self._kwargs['values']['transmission_delay'])

