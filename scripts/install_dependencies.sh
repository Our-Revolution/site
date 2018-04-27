#!/bin/bash

echo "Start installing dependencies"
cd /home/ubuntu/ourrevolution
source $(which virtualenvwrapper.sh)
workon ourrevolution

echo "npm install..."
npm install

echo "pip install..."
pip install -r requirements.txt

echo "Finished installing dependencies"
