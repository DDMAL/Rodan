#!/bin/bash

. rodan_env/bin/activate
python manage.py runfcgi --settings rodan.settings-production daemonize=false socket=/tmp/rodan.sock
