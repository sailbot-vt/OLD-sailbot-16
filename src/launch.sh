#!/bin/bash

print_message() {
	echo '\033[36m\033[1m'$1'\033[0m\033[39m'
}

print_message 'Starting SailBOT'

print_message 'Creating GPSD TCP Socket...'
./modules/pgps 8907 &

print_message 'Creating Wind Sensor TCP Socket...'
sudo python "modules/wind_sensor.py" &

print_message 'Creating Rudder TCP Socket...'
sudo python "modules/servo.py" 9107 18 1.5 1.2 &

print_message 'Launching main program...'
sudo python3 main.py
