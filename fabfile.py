from fabric.api import *

def up(port="8001"):
    local("python manage.py runserver 0.0.0.0:%s"%port)

def reset():
    with settings(warn_only=True):
        local("rm db.sqlite")
    local("python manage.py syncdb --noinput")

def dump():
    with hide('running', 'status'):
        local("python manage.py dumpdata rodan --indent=4")

def celery():
    local("python manage.py celeryd -E --autoreload --loglevel=DEBUG")

def test():
    local("python manage.py test rodan")
