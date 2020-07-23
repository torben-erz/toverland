#!/bin/bash

echo ""
echo "Welcome to Toverland-Wand Installation Script for Raspbian"
echo "Maintained by Torben Daniel Erz (torben.erz@gmail.com)"


# Step 1: Preparing
echo ""
echo "================================"
echo "Preparing system for installation ..."

sudo apt-get -y update
sudo apt-get -y upgrade


# Step 2: Download scripts
echo ""
echo "================================"
echo "Downloading scripts ..."
wget https://raw.githubusercontent.com/torben-erz/raspberry-pi-scripts/master/gpio.sh
wget https://raw.githubusercontent.com/torben-erz/raspberry-pi-scripts/master/picamera.sh


# Step 3: Execute installation script GPIO
echo ""
echo "================================"
echo "Execute Installation of GPIO ..."
sh ./install_gpio.sh


# Step 4: Execute installation script PiCamera
echo ""
echo "================================"
echo "Execute Installation of PiCamera ..."
sh ./install_picamera.sh


# Step 5: Download and install software
echo ""
echo "================================"
echo "Download and install software ..."
wget https://raw.githubusercontent.com/torben-erz/toverland-wand/master/toverland.zip -O toverland.zip
if [ toverland ]; then
    rm -rf toverland
fi
unzip -O toverland.zip


# Step 6: Delete downloads
rm install_gpio.sh
rm install_picamera.sh
rm toverland.zip


echo ""
echo "Complete - will reboot in 5 sec. ..."
sleep 5


# Reboot
#sudo reboot
