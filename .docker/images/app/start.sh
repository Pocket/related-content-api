#! /usr/bin/env sh
set -e

#  https://github.com/tiangolo/uvicorn-gunicorn-docker
#
#  The MIT License (MIT)
#
#  Copyright (c) 2019 Sebastián Ramírez
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:

#if [ -f /app/app/main.py ]; then
#    DEFAULT_MODULE_NAME=app.main
#elif [ -f /app/main.py ]; then
#    DEFAULT_MODULE_NAME=main
#fi
#MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
#VARIABLE_NAME=${VARIABLE_NAME:-app}
#export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}
#
#if [ -f /app/gunicorn_conf.py ]; then
#    DEFAULT_GUNICORN_CONF=/app/gunicorn_conf.py
#elif [ -f /app/app/gunicorn_conf.py ]; then
#    DEFAULT_GUNICORN_CONF=/app/app/gunicorn_conf.py
#else
#    DEFAULT_GUNICORN_CONF=/gunicorn_conf.py
#fi
#export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}
#export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}
#
## If there's a prestart.sh script in the /app directory or other path specified, run it before starting
#PRE_START_PATH=${PRE_START_PATH:-/app/prestart.sh}
#echo "Checking for script in $PRE_START_PATH"
#if [ -f $PRE_START_PATH ] ; then
#    echo "Running script $PRE_START_PATH"
#    . "$PRE_START_PATH"
#else
#    echo "There is no script $PRE_START_PATH"
#fi

# Start Gunicorn
#exec gunicorn -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"
# TODO: CHANGE THIS BEFORE GOING TO PRODUCTION
cd /app/src && flask run