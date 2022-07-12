#!/bin/bash
#### ONLY FOR DEVELOPMENT USE!!!
python3.7 manage.py sqlflush | python3.7 manage.py dbshell
