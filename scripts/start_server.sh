#!/bin/bash

echo "Start script for starting server"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
workon ourrevolution

echo "Start server"
supervisorctl start gunicorn

if [ "$DEPLOYMENT_GROUP_NAME" == "Production" ]
then
    echo "Start varnish"
    sudo service varnish start
else
    echo "Skip varnish"
fi

echo "Server started"
