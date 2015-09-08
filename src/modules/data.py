
import socket, logging, json, time

from .log import WebSocketLogger
from .utils import getJSON
from .control_thread import StoppableThread
from .server import ServerThread
from .utils import SocketType, socket_connect
from contextlib import contextmanager

logger = logging.getLogger('log')

@contextmanager
def query(socket):
    try:
        socket.send(str(0).encode('utf-8'))
        parsed = json.loads(socket.recv(256).decode('utf-8').strip('\x00'))
        yield parsed
    except (AttributeError, ValueError, BrokenPipeError) as e:
        logger.error("A socket is broken!")
        yield ''

class DataThread(StoppableThread):

    server_thread = rudder_sock = winch_sock = None

    def __init__(self, *args, **kwargs):
        super(DataThread, self).__init__(*args, **kwargs)
        global server_thread, rudder_sock, winch_sock

        server_thread = ServerThread(
            name = 'Server',
            kwargs = {
                'port': self._kwargs['values']['port'],
                'target_locations': self._kwargs['values']['target_locations'],
                'boundary_locations': self._kwargs['values']['boundary_locations']
                }
            )

        server_thread.start()
        rudder_sock = socket_connect(SocketType.rudder)
        winch_sock = socket_connect(SocketType.winch)

    def set_angle(self, angle, socket_type):
        try:
            if socket_type == SocketType.rudder:
                rudder_sock.send(str(angle).encode('utf-8'))
            elif socket_type == SocketType.winch:
                winch_sock.send(str(angle).encode('utf-8'))
        except socket.error:
            logger.error('A servo socket is broken!')

    def run(self):
        logger.info('Starting the data thread!')

        gps_sock = socket_connect(SocketType.gps)
        wind_sock = socket_connect(SocketType.wind)
        data = self._kwargs['data']

        while True:
            if self.stopped():
                server_thread.stop()
                break

            with query(gps_sock) as parsed:
                data.update(parsed)
                if all (k in parsed for k in ('latitude', 'longitude')):
                    data['location'] = {'latitude': parsed['latitude'], 'longitude': parsed['longitude']}

            with query(wind_sock) as parsed:
                if not parsed == '':
                    data['wind_dir'] = parsed

            server_thread.send_data(getJSON(data))
            logger.debug('Data sent to the server %s' % json.dumps(json.loads(getJSON(data))))
            time.sleep(self._kwargs['values']['transmission_delay'])
