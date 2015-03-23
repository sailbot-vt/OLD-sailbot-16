#!/usr/bin/python

import time
import logging

import smbus
import threading
import socket
import sys
from thread import *
import time
import json
import threading

wind_sensor = None  # global wind_sensor variable
angle = 0.0;

# define the socket parameters
HOST = ''
PORT = 8807

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

# bind socket to local host and port
try:
    connection.bind((HOST, PORT))
except socket.error, msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' \
        + msg[1]
    sys.exit()

print 'Socket bind complete'

class WindSensor(threading.Thread):

    address = 0x48  # Address the port runs on
    analogs = [0x4000, 0x5000, 0x6000, 0x7000]
    normal = 0x0418


    max = 1200.0
    min = 200.0

    def switch_bits(self, input):
        # Flips the bits of the input and returns the result
        return (input >> 8) + ((input & 0x00ff) << 8)


    def set_data_channel(self, input, bus):
        bus.write_word_data(address, 0x01, 0x1C40)
        time.sleep(0.01)


    def read_data(self, bus):
        # Read data from the bus
        time.sleep(0.01)
        return self.switch_bits(bus.read_word_data(address, 0)) >> 4


    def setup(self, input, bus):
        # Write values to the registers
        bus.write_word_data(address, 0x02, self.switch_bits(input << 4))
        time.sleep(0.01)
        bus.write_word_data(address, 0x03, self.switch_bits(0x7fff))
        time.sleep(0.01)


    def calculate_angle(self, input):
        global max, min

        # Alter the maximum and minimum values during calibration
        if input > max:
            max = input

        if input < min:
            min = input

        a = max - min

        # Return the measured value as a proportionally scaled angle
        return (input - min) * (360.0 / a)

    def run(self):
        global angle    # Bring the angle into scope

        try:
            bus = smbus.SMBus(1)
            self.setup(1500, bus)
            self.set_data_channel(analogs[0], bus)

            while True:
                angle = calculate_angle(readData(bus));
                time.sleep(0.1)
                
        except NameError:
            print('SMBUS is not correctly configured!')
            return

            
# create and start the wind_sensor thread
wind_sensor = WindSensor()
wind_sensor.start()

# Start listening on socket
connection.listen(10)
print 'Socket now listening'

# function for handling connections; will be used to create threads
def clientthread(conn):

    # infinite loop so that function do not terminate and thread do not end
    while True:

        # receive data from the client
        data = conn.recv(1024)
        if not data:
            break
        print 'Received %s from the server.' % data

        if data == '0':
            print 'Sending: %s' % angle
            conn.sendall(angle)

    # close the connection if the client if the client and server connection is interfered
    conn.close()

# main loop to keep the server process going
while True:

    # wait to accept a connection in a blocking call
    (conn, addr) = connection.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function

    start_new_thread(clientthread, (conn, ))

connection.close()

            