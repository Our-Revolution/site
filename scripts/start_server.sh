#!/bin/bash

# Handle errors http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -eo pipefail
IFS=$'\n\t'

echo "Start script for starting server"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
# TODO: TECH-1294 debug error code
workon ourrevolution || true

# Check if task handler is disabled
if [ "$DISABLE_TASK_HANDLER" != "1" ]
then
  echo "Restart celery"
  # Stop celery main process gracefully and auto-restart
  # TODO: TECH-1294 debug error code
  celery -A ourrevolution inspect stats | grep '"pid": ' | awk '{print $2}' | awk -F, '{print $1}' | xargs kill -TERM || true
fi

# Check if web app is disabled
if [ "$DISABLE_WEB_APP" != "1" ]
then
  echo "Start web app"
  supervisorctl start gunicorn

  echo "Purge Fastly"
  curl -XPOST -H "Fastly-Key:$FASTLY_API_KEY" https://api.fastly.com/service/$FASTLY_SERVICE_ID/purge_all
fi

echo "Server started"
