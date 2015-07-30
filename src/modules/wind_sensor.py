#!/usr/bin/python
import time, logging, sys, socket, json, threading
from thread import *
from utils import setup_logging

class WindSocket():

    def __init__(self, name):
        logger = logging.getLogger('log')
        setup_logging()

        try:
            import smbus
        except ImportError:
            logger.critical('[Wind Sensor Socket]: SMBUS not configured properly!')
            sys.exit(1)

        wind_sensor = None  # Global wind_sensor variable
        angle = 0.0

        # Define the socket parameters
        HOST = ''
        PORT = 8894

        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind socket to local host and port
        try:
            connection.bind((HOST, PORT))
        except socket.error, msg:
            logger.critical('[Wind Sensor Socket]: Bind failed. Error Code: ' + str(msg[0]) + ' Message ' \
                + msg[1])
            sys.exit()

        logger.debug('[Wind Sensor Socket]: Socket bind complete!')

        self.start_socket_process()

    class WindSensor(threading.Thread):

        address = 0x48  # Address the port runs on
        analogs = [0x4000, 0x5000, 0x6000, 0x7000]
        normal = 0x0418

        max = 1200.0
        min = 200.0

        # Flips the bits of the input and returns the result
        def switch_bits(self, input):
            return (input >> 8) + ((input & 0x00ff) << 8)

        def set_data_channel(self, input, bus):
            bus.write_word_data(self.address, 0x01, 0x1C40)
            time.sleep(0.01)

        # Read data from the bus
        def read_data(self, bus):
            time.sleep(0.01)
            return self.switch_bits(bus.read_word_data(self.address, 0)) >> 4

        # Write values to the registers
        def setup(self, input, bus):
            bus.write_word_data(self.address, 0x02, self.switch_bits(input << 4))
            time.sleep(0.01)
            bus.write_word_data(self.address, 0x03, self.switch_bits(0x7fff))
            time.sleep(0.01)

        # Alter the maximum and minimum values during calibration
        def calculate_angle(self, input):
            if input > self.max:
                self.max = input

            if input < self.min:
                self.min = input

            a = self.max - self.min

            # Return the measured value as a proportionally scaled angle
            return (input - self.min) * (360.0 / a)

        def run(self):
            global angle  # Bring the angle into scope

            logger.warn('[Wind Sensor Socket]: Remember to calibrate the wind sensor before use!')

            try:
                bus = smbus.SMBus(0x01)
                self.setup(1500, bus)
                self.set_data_channel(self.analogs[0], bus)

                while True:
                    angle = self.calculate_angle(self.read_data(bus))
                    time.sleep(0.1)
            except IOError:
                logger.critical('[Wind Sensor Socket]: IO Error: device cannot be read, check your wiring or run as root')

    def start_socket_process():
        # Create and start the wind_sensor thread
        wind_sensor = WindSensor()
        wind_sensor.daemon = True # Needed to make the thread shutdown correctly
        wind_sensor.start()

        # Start listening on socket
        connection.listen(10)

        # Function for handling connections; will be used to create threads
        def clientthread(conn):
            # Infinite loop so that function do not terminate and thread do not end
            while True:
                # Receive data from the client
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(json.dumps(angle).encode('utf-8'))

            # Close the connection if the client if the client and server connection is interfered
            conn.close()

        # Main loop to keep the server process going
        while True:
            try:
                # Wait to accept a connection in a blocking call
                (conn, addr) = connection.accept()
                logger.debug('[Wind Sensor Socket]: Connected with ' + addr[0] + ':' + str(addr[1]))

                # Start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function
                start_new_thread(clientthread, (conn, ))

            except KeyboardInterrupt, socket.error:
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
                break

WindSocket(sys.argv[1])
