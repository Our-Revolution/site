#!/bin/bash

echo "Start installing dependencies"
cd /home/ubuntu/ourrevolution
source $(which virtualenvwrapper.sh)
workon ourrevolution

echo "Install build tools"
npm install

echo "Install package requirements from requirements.txt"
pip install -r requirements.txt

echo "Finished installing dependencies"
