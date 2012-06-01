from fabric.api import *

def up():
    local("python manage.py runserver 0.0.0.0:8001")

def reset():
    with settings(warn_only=True):
        local("rm db.sqlite")
    local("echo 'no' | python manage.py syncdb")

def test():
    local("python manage.py test rodan")
