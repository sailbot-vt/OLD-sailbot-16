#!/bin/bash

echo '\033[36m\033[1mStarting SailBOT Build Script...\033[0m\033[39m'

echo '\033[36m\033[1mUpdating Raspberry Pi...\033[0m\033[39m'
sudo apt-get update

echo '\033[36m\033[1mInstalling Python 3, GPSD, and I2C Dependencies...\033[0m\033[39m'
sudo apt-get install build-essential python3-dev gpsd gpsd-clients python-gps i2c-tools python-smbus python-pip

echo '\033[36m\033[1mRefreshing packages...\033[0m\033[39m'
sudo apt-get update

echo '\033[36m\033[1mSetting up Tornado Web Server...\033[0m\033[39m'
sudo pip install tornado

echo '\033[36m\033[1mPulling project from repository...\033[0m\033[39m'
cd ~/
mkdir SailBOT
cd SailBOT
git clone https://github.com/jamestaylr/sailbot.git

