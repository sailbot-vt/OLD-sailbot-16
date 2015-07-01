
import socket, logging, json, time

from .log import WebSocketLogger
from .utils import getJSON
from .control_thread import StoppableThread
from .server import ServerThread
from .utils import SocketType, socket_connect

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
        rudder_sock = socket_connect(SocketType.rudder)

        global winch_sock
        winch_sock = socket_connect(SocketType.winch)


    def set_angle(self, connection, angle):
        try:
            rudder_sock.send(str(angle).encode('utf-8'))
        except socket.error:
            # Broken Pipe Error
            logger.error('The servo socket is broken!')

    def set_rudder_angle(self, angle):
        self.set_angle(rudder_sock, angle)

    def set_winch_angle(self, angle):
        self.set_angle(winch_sock, angle)

    def send_data(self, data):
        try:
            server_thread.send_data(self._kwargs['data'])
        except tornado.websocket.WebSocketClosedError:
            print('Could not send data because the socket is closed.')

    def run(self):

        logger.info('Starting the data thread!')

        gps_sock = socket_connect(SocketType.gps)
        wind_sock = socket_connect(SocketType.wind)

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
