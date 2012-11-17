import djcelery

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'rodan.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/mnt/images/'

djcelery.setup_loader()
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "rodanuser"
BROKER_PASSWORD = "DDMALrodan"
BROKER_VHOST = "DDMAL"
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

CELERY_RESULT_BACKEND = "database"
#Note: If youre using SQLite as the Django database backend, celeryd will only be able to process one task at a time,
#this is because SQLite doesnt allow concurrent writes.
CELERY_RESULT_DBURI = "sqlite:///db.sqlite"

SOLR_URL = 'http://rodan.simssa.ca:8080/rodan-search-dev'
IIP_URL = 'http://rodan.simssa.ca/fcgi-bin/iipsrv.fcgi'

CLASSIFIER_XML = 'salzinnes_demo_classifier.xml'
