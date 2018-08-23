#!/bin/bash

# Handle errors http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -eo pipefail
IFS=$'\n\t'

echo "Start installing packages"
cd /home/ubuntu/ourrevolution
source /home/ubuntu/.virtualenvs/ourrevolution/bin/virtualenvwrapper.sh
# TODO: TECH-1294 debug error code
workon ourrevolution || true

echo "Install front end packages"
npm install

echo "Build front end assets"
sudo chown ubuntu -R pages/static/dist/
gulp build --production

echo "Install package requirements from requirements.txt"
easy_install distribute
pip install -r requirements.txt

echo "Collect static files"
sudo chown ubuntu -R .static/
./manage.py collectstatic --noinput

echo "Finished installing packages"
