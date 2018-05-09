#!/bin/bash

echo "Start script for starting server"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
workon ourrevolution

echo "Start server"
supervisord -c supervisord.conf
supervisorctl start gunicorn

echo "Server started"
