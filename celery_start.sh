#!/bin/bash

VIRTUAL_ENV=/home/rodan/rodan_env	# name of virtual_env directory
source ${VIRTUAL_ENV}/bin/activate
exec ${VIRTUAL_ENV}/bin/celery -A rodan worker -l DEBUG 
