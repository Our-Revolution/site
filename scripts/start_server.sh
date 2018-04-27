#!/bin/bash

echo "Start script for starting server"
cd /home/ubuntu/ourrevolution
source $(which virtualenvwrapper.sh)
workon ourrevolution

echo "Start server"
supervisorctl start gunicorn

echo "Server started"
