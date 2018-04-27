#!/bin/bash

echo "Start server"
cd /home/ubuntu/ourrevolution
supervisorctl start gunicorn

echo "Server started"
