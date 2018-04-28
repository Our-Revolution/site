#!/bin/bash

echo "Start before install script"
cd /home/ubuntu/ourrevolution

echo "Remove old git files"
find . -type f -not -name 'gunicorn_error.log' -not -name 'supervisord.log' -not -name 'supervisord.pid' -delete

echo "Finished script for before install"
