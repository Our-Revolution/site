#!/bin/bash

echo "Start script for stopping server"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
workon ourrevolution

if [ "$DEPLOYMENT_GROUP_NAME" == "QA" ]
then
    echo qa deployment group: $DEPLOYMENT_GROUP_NAME
else
    echo not qa deploy group
fi

if [ "$DEPLOYMENT_GROUP_NAME" == "Production" ]
then
    echo Production deployment group: $DEPLOYMENT_GROUP_NAME
else
    echo not Production deploy group
fi

echo "Stop server"
supervisord -c supervisord.conf
supervisorctl stop gunicorn

echo "Finished script for stopping server"
