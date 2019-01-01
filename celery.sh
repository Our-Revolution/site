#!/bin/bash
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
workon ourrevolution

# Check if task handler is disabled
if [ "$DISABLE_TASK_HANDLER" != "1" ]
then
    # TODO: TECH-1649: debug env var issue
    exec celery worker -A ourrevolution --loglevel=INFO --concurrency=1 --max-tasks-per-child=1 --broker=$CELERY_BROKER_URL --result-backend=$CELERY_RESULT_BACKEND
fi
