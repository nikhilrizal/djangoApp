#!/bin/bash

# migrate
python src/manage.py migrate

if [ -n "$RUN_TASK" ]; then
    PYTHONPATH=src python src/manage.py $RUN_TASK
else
    PYTHONPATH=src gunicorn texttointerface.wsgi:application --bind 0.0.0.0:80 --timeout 600 --workers 3
fi