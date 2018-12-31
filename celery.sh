#!/bin/bash
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
workon ourrevolution
# TODO: check if task machine mode is enabled
exec celery worker -A ourrevolution --loglevel=INFO --concurrency=1 --max-tasks-per-child=1 --broker=$CELERY_BROKER_URL --result-backend=$CELERY_RESULT_BACKEND
