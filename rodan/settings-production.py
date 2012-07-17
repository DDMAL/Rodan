# Django settings for rodan project.
from settings import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rodan',
        'USER': 'rodan',
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/mnt/images/'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'rodan.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rodan',
    'djcelery',
    'rodan.jobs',
)

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "rodanuser"
BROKER_PASSWORD = "DDMALrodan"
BROKER_VHOST = "DDMAL-production"
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = "postgresql://rodan@localhost/rodan"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

SOLR_URL = 'http://rodan.simssa.ca:8080/rodan-search-dev'
IIP_URL = 'http://rodan.simssa.ca/fcgi-bin/iipsrv.fcgi'

CLASSIFIER_XML = 'salzinnes_demo_classifier.xml'
