#!/usr/bin/python
import time
import logging

try:
    import smbus
except ImportError:
    # Do not log ImportError, as logging has not been configured yet
    pass

import threading

class WindSensor(threading.Thread):

    address = 0x48  # Address the port runs on
    analogs = [0x4000, 0x5000, 0x6000, 0x7000]
    normal = 0x0418

    angle = 0.0;

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
                print('Read: %d as %d' % (readData(bus),
                                          calculate_angle(readData(bus))))

                self._kwargs['data']['angle'] = calculate_angle(readData(bus));
                time.sleep(0.1)
                
        except NameError:
            logging.critical('SMBUS is not correctly configured!')
            return

			