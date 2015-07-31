#!/bin/bash

print_message() {
	echo '\033[36m\033[1m'$1'\033[0m\033[39m'
}

print_message 'Configuring GPSD...'
sudo killall gpsd
sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
