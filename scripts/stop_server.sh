#!/bin/bash

echo "Stop server"
cd /home/ubuntu/ourrevolution
supervisorctl stop gunicorn

echo "Server stopped"
