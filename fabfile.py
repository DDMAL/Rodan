from fabric.api import *

def up():
    local("python manage.py runserver 0.0.0.0:8001")

def reset():
    with settings(warn_only=True):
        local("rm db.sqlite")
    local("python manage.py syncdb --noinput")

def dump():
    local("python manage.py dumpdata rodan --indent=4")

def test():
    local("python manage.py test rodan")
