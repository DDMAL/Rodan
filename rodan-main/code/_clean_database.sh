#!/bin/bash
#### ONLY FOR DEVELOPMENT USE!!!
python3 manage.py sqlflush | python3 manage.py dbshell
