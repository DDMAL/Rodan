#!/bin/bash

. rodan_env/bin/activate
python manage.py runfcgi daemonize=false socket=/tmp/rodan.sock
