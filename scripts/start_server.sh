#!/bin/bash

# Handle errors http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -eo pipefail
IFS=$'\n\t'

echo "Start script for starting server"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
# TODO: TECH-1294 debug error code
workon ourrevolution || true

echo "Restart Celery"
supervisorctl restart celery

echo "Start server"
supervisorctl start gunicorn

echo "Start varnish"
sudo service varnish start

echo "Purge Fastly"
curl -XPOST -H "Fastly-Key:$FASTLY_API_KEY" https://api.fastly.com/service/$FASTLY_SERVICE_ID/purge_all

echo "Server started"
