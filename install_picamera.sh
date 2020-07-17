#!/bin/bash

echo ""
echo "================================"
echo "Welcome to PiCamera Installation Script for Raspbian"
echo "Maintained by Torben Daniel Erz (torben.erz@gmail.com)"
echo ""

# Step 1: Preparing
echo ""
echo "================================"
echo "Preparing system for installation..."

sudo apt-get -y update
sudo apt-get -y upgrade

echo ""
echo "Complete"
echo ""

# Step 2: Install PiCamera
echo ""
echo "================================"
echo "Installing pigpio"
sudo apt-get -y install python-picamera python3-picamera

echo ""
echo "Complete"
echo ""

echo "================================"
echo "The installation of PiCamera was successful"
echo ""
echo "ATTENTION: Please activate the camera interface in the Raspberry Pi settings!!!"
echo "TESTING: Enter the following in the command line: raspistill -o sample.jpg"
echo ""
