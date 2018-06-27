#!/bin/bash

# Handle errors http://redsymbol.net/articles/unofficial-bash-strict-mode/
# set -euo pipefail
# IFS=$'\n\t'

# Test error - remove after done testing
grep static lebowski

echo "Start script for stopping server"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
workon ourrevolution

if [ "$DEPLOYMENT_GROUP_NAME" == "Production" ]
then
    echo "Stop varnish"
    sudo service varnish stop
else
    echo "Skip varnish"
fi

echo "Stop server"
supervisorctl stop gunicorn

echo "Finished script for stopping server"
