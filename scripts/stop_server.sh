#!/bin/bash

echo "Start script for stopping server"
cd /home/ubuntu/ourrevolution
source $(which virtualenvwrapper.sh)
workon ourrevolution

echo "Stop server"
supervisorctl stop gunicorn

echo "Finished script for stopping server"
