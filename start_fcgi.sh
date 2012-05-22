#!/bin/bash

. rodan_env/bin/activate
python manage.py runfcgi --settings daemonize=false socket=/tmp/rodan.sock
