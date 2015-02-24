#!/bin/bash

echo '\033[94m\033[1mStarting SailBOT Build Script...\033[0m\033[39m'

echo '\033[94m\033[1mUpdating Raspberry Pi...\033[0m\033[39m'
sudo apt-get update
echo '\033[94m\033[1mInstalling Python 3 Developer Packages...\033[0m\033[39m'
sudo apt-get install build-essential python3-dev
sudo apt-get update
echo '\033[94m\033[1mInstalling GPS and GPSD Packages...\033[0m\033[39m'
sudo apt-get install gpsd gpsd-clients python-gps
sudo apt-get update

echo '\033[94m\033[1mFetching Tornado Web Server...\033[0m\033[39m'
cd ~/
wget https://pypi.python.org/packages/source/t/tornado/tornado-4.1.tar.gz
tar xvzf tornado-4.1.tar.gz
cd tornado-4.1
echo '\033[94m\033[1mBuilding Tornado Web Server...\033[0m\033[39m'
python3 setup.py build
sudo python3 setup.py install

echo '\033[94m\033[1mCleaning up installation...\033[0m\033[39m'
cd ..
rm -r tornado-4.1/
rm tornado-4.1.tar.gz

echo '\033[94m\033[1mPulling project from repository...\033[0m\033[39m'
cd ~/
mkdir SailBOT
cd SailBOT
git clone https://github.com/jamestaylr/sailbot.git

