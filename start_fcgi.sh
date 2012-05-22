#!/bin/bash

. rodan_env/bin/activate
python manage.py runfcgi socket=/tmp/rodan.sock
