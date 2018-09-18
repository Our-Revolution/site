#!/bin/bash

# Handle errors http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -eo pipefail
IFS=$'\n\t'

echo "Start script for starting server"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
# TODO: TECH-1294 debug error code
workon ourrevolution || true

echo "Restart celery"
# Stop celery main process gracefully and auto-restart
celery -A ourrevolution inspect stats | grep '"pid": ' | awk '{print $2}' | awk -F, '{print $1}' | xargs kill -TERM

echo "Start server"
supervisorctl start gunicorn

echo "Purge Fastly"
curl -XPOST -H "Fastly-Key:$FASTLY_API_KEY" https://api.fastly.com/service/$FASTLY_SERVICE_ID/purge_all

echo "Server started"
