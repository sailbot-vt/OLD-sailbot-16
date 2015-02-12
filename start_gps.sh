#!/bin/bash

echo '\033[36mStarting the GPS Python daemon\033[39m'
sudo killall gpsd
sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
sudo python "src/modules/gps.py"