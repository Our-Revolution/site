#!/bin/bash

# Handle errors http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -eo pipefail
IFS=$'\n\t'

echo "Start script for stopping server"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
# TODO: TECH-1294 debug error code
workon ourrevolution || true

# Check if web app is disabled
if [ "$DISABLE_WEB_APP" != "1" ]
then
  echo "Stop server"
  supervisorctl stop gunicorn
fi

echo "Finished script for stopping server"
