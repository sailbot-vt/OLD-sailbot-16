#!/usr/bin/python
import socket, sys, time, json, threading, logging
from thread import *
from utils import setup_logging

class ServoController():
    class Servo():
        def blink(self, angle, pin, scale_factor, zero_point, ticks):
            a = (((angle)/180.0) * scale_factor + zero_point)/1000.0

            for i in range(0, ticks):

                GPIO.output(pin, True)
                time.sleep(a)

                GPIO.output(pin, False)
                # Time between pulses
                time.sleep(0.015)

    def __init__(self, name, port, pin, scale_factor, zero_point):
        logger = logging.getLogger('log')
        setup_logging(name)

        try:
            import RPi.GPIO as GPIO
        except ImportError:
            logger.critical('[Servo Socket]: GPIO not configured properly!')
            sys.exit(1)

        self.port = port
        self.pin = pin
        self.scale_factor = scale_factor
        self.zero_point = zero_point

        # Configure the servo
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.OUT)

        # Define the socket parameters
        HOST = ''
        PORT = self.port

        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind socket to local host and port
        try:
            connection.bind((HOST, PORT))
        except socket.error, msg:
            logger.critical('[Servo Socket]: Bind failed. Error Code: ' + str(msg[0]) + ' Message ' \
                + msg[1])
            sys.exit()

        print '[Servo Socket]: Socket bind complete!'

        # Create a pointer to the servo class
        servo = self.Servo()

        # Start listening on socket
        connection.listen(10)

        # Function for handling connections; will be used to create threads
        def clientthread(conn):

            # Infinite loop so that function do not terminate and thread do not end
            while True:
                # Receive data from the client
                data = conn.recv(16)
                if not data:
                    break

                try:
                    servo.blink(float(data), self.pin, self.scale_factor, self.zero_point, 10)
                except ValueError:
                   logger.critical('[Servo Socket]: Recieved extraneous angle value: %s' % data)

            # Close the connection if the client if the client and server connection is interfered
            conn.close()

        # Main loop to keep the server process going
        while True:
            try:
                # Wait to accept a connection in a blocking call
                (conn, addr) = connection.accept()
                print '[Servo Socket]: Connected with ' + addr[0] + ':' + str(addr[1])

                # Start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function
                start_new_thread(clientthread, (conn, ))

            except KeyboardInterrupt, socket.error:
                GPIO.cleanup()
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
                break

ServoController(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
