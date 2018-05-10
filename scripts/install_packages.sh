#!/bin/bash

echo "Start installing packages"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
workon ourrevolution

echo "Install build tools"
npm install
# gulp build --production

echo "Install package requirements from requirements.txt"
easy_install distribute
pip install -r requirements.txt

echo "Collect static files"
sudo chown ubuntu -R .static/
./manage.py collectstatic --noinput

echo "Finished installing packages"
