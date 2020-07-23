#!/bin/bash

echo ""
echo "Welcome to Toverland-Wand Installation Script for Raspbian"
echo "Maintained by Torben Daniel Erz (torben.erz@gmail.com)"


# Step 1: Preparing
echo ""
echo "================================"
echo "Preparing system for installation ..."
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade --fix-missing -y
sudo apt autoremove


# Step 2: Download scripts
echo ""
echo "================================"
echo "Downloading scripts ..."
wget https://raw.githubusercontent.com/torben-erz/raspberry-pi-scripts/master/python3.sh
wget https://raw.githubusercontent.com/torben-erz/raspberry-pi-scripts/master/gpio.sh
wget https://raw.githubusercontent.com/torben-erz/raspberry-pi-scripts/master/picamera.sh


# Step 3: Execute installation script Python 3
echo ""
echo "================================"
echo "Execute Installation of Python 3 ..."
sh ./python3.sh


# Step 4: Execute installation script GPIO
echo ""
echo "================================"
echo "Execute Installation of GPIO ..."
sh ./gpio.sh


# Step 5: Execute installation script PiCamera
echo ""
echo "================================"
echo "Execute Installation of PiCamera ..."
sh ./picamera.sh


# Step 6: Download and install software
echo ""
echo "================================"
echo "Download and install software ..."
wget https://raw.githubusercontent.com/torben-erz/toverland-wand/master/toverland.zip -O toverland.zip
if [ toverland ]; then
    rm -rf toverland
fi
unzip -o toverland.zip


# Step 7: Delete downloads
rm python3.sh
rm gpio.sh
rm picamera.sh
rm toverland.zip


echo ""
echo "Complete - will reboot in 5 sec. ..."
sleep 5


# Reboot
sudo reboot
