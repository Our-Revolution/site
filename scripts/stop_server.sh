#!/bin/bash

# Handle errors http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -eo pipefail
IFS=$'\n\t'

echo "Start script for stopping server"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
# TODO: TECH-1294 debug error code
workon ourrevolution || true

echo "Stop Celery"
# Stop main process only with graceful shutdown so worker tasks can finish
celery -A ourrevolution inspect stats | grep '"pid": ' | awk '{print $2}' | awk -F, '{print $1}' | xargs kill -TERM

echo "Stop server"
supervisorctl stop gunicorn

echo "Finished script for stopping server"
