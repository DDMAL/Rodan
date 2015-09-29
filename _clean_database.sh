#!/bin/bash
#### ONLY FOR DEVELOPMENT USE!!!
python manage.py sqlflush | python manage.py dbshell
