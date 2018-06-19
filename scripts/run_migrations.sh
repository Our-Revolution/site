#!/bin/bash

echo "Start running migrations"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
workon ourrevolution

echo "Run migrations"
./manage.py migrate --noinput

echo "Finished running migrations"
