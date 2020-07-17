#!/bin/bash

echo ""
echo "================================"
echo "Welcome to OpenCV 4.0.1 Installation Script for Raspbian"
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


# Step 2: Install dependencies
echo ""
echo "================================"
echo "Installing dependencies ..."
sudo apt-get -y install libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test

echo ""
echo "Complete"
echo ""


# Step 3: Install OpenCV
echo ""
echo "================================"
echo "Installing OpenCV 4.0.1 ..."
pip3 install opencv-python==4.0.1.24

echo ""
echo "Complete"
echo ""

# Step 4: ITesting
echo ""
echo "The installation of OpenCV was successful and the version is:"
python3 -c "import cv2; print(cv2.__version__)"
echo ""
