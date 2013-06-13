import djcelery
djcelery.setup_loader()

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'rodan.sqlite3',
        #'USER': 'ahankins',
        #'PASSWORD': '',
        #'HOST': 'localhost',
        #'PORT': '5432'
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/mnt/images/'
BROKER_URL = 'amqp://rodanuser:DDMALrodan@localhost:5672/DDMAL'
CELERY_IMPORTS = ("rodan.helpers.thumbnails",
                  "rodan.helpers.convert",
                  "rodan.helpers.pagedone",
                  "rodan.jobs.gamera.celery_task")

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

CELERY_RESULT_BACKEND = "amqp"
#Note: If youre using SQLite as the Django database backend, celeryd will only be able to process one task at a time,
#this is because SQLite doesnt allow concurrent writes.
# CELERY_RESULT_DBURI = "sqlite:///db.sqlite"

SOLR_URL = 'http://rodan.simssa.ca:8080/rodan-search-dev'
IIP_URL = 'http://rodan.simssa.ca/fcgi-bin/iipsrv.fcgi'

CLASSIFIER_XML = 'salzinnes_demo_classifier.xml'
