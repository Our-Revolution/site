#!/bin/bash

echo "Start installing packages"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
workon ourrevolution

echo "Install build tools"
npm install

echo "Install package requirements from requirements.txt"
pip install -r requirements.txt

echo "Collect static files"
./manage.py collectstatic --noinput

echo "Finished installing packages"