#!/bin/bash

# Handle errors http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

# Test error - remove after done testing
grep static lebowski

echo "Start before install script"
cd /home/ubuntu/ourrevolution

echo "Remove old git files"
sudo find . -not -name 'gunicorn_error.log' -not -name 'supervisord.log' -not -name 'supervisord.pid' -not -name 'django-debug.log' -not -path './node_modules' -not -path './node_modules/*' -delete

echo "Finished script for before install"
