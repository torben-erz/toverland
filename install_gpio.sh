#!/bin/bash

echo ""
echo "================================"
echo "Welcome to pigpio Installation Script for Raspbian"
echo "Maintained by Torben Daniel Erz (torben.erz@gmail.com)"
echo ""


# Step 1: Preparing
echo ""
echo "================================"
echo "Preparing system for installation..."


# Clean build directories
rm -rf master.zip
rm -rf pigpio-master

sudo apt-get -y update
sudo apt-get -y upgrade

echo ""
echo "Complete"
echo ""


# Step 2: Install pigpio library
echo ""
echo "================================"
echo "Installing pigpio library"

# Stop daemon
sudo systemctl stop pigpiod

wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
rm -rf master.zip
cd pigpio-master
make
sudo make install

echo ""
echo "Complete"
echo ""


# Step 3: Install pigpio
echo ""
echo "================================"
echo "Installing pigpio"
sudo apt-get -y install pigpio python3-pigpio python3-rpi-gpio

# Start ans enable daemon
sudo systemctl start pigpiod
sudo systemctl enable pigpiod

echo ""
echo "Complete"
echo ""

echo "================================"
echo "The installation of pigpio was successful"
echo ""
echo "ATTENTION: Please reboot the Raspberry Pi!!!"
echo ""
echo "TESTING: "
echo "$ pigs modes 25 w"
echo "$ pigs w 25 1"
echo "$ pigs w 25 0"
