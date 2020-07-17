#!/bin/bash

echo ""
echo "================================"
echo "Welcome to Toverland-Pi Installation Script for Raspbian"
echo "Maintained by Torben Daniel Erz (torben.erz@gmail.com)"
echo ""


# Step 1: Preparing
echo ""
echo "================================"
echo "Preparing system for installation ..."

sudo apt-get -y update
sudo apt-get -y upgrade

echo ""
echo "Complete"
echo ""


# Step 2: Download scripts
echo ""
echo "================================"
echo "Downloading scripts ..."
wget https://raw.githubusercontent.com/torben-erz/toverland/master/install_opencv4.sh
wget https://raw.githubusercontent.com/torben-erz/toverland/master/install_gpio.sh
wget https://raw.githubusercontent.com/torben-erz/toverland/master/install_picamera.sh


# Step 3: Execute installation script OpenCV
echo ""
echo "================================"
echo "Execute Installation of OpenCV ..."
sh ./install_opencv4.sh


# Step 4: Execute installation script GPIO
echo ""
echo "================================"
echo "Execute Installation of GPIO ..."
sh ./install_gpio.sh


# Step 5: Execute installation script PiCamera
echo ""
echo "================================"
echo "Execute Installation of PiCamera ..."
sh ./install_picamera.sh


# Step 5: Delete sh-scripts
rm -rf install_opencv4.sh
rm -rf install_gpio.sh
rm -rf install_picamera.sh


# Step 5: Install Python3 IDLE
sudo apt-get -y install idle3
