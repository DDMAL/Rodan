"""
Rodan settings. Remember to set your environment variables.
"""
import os
import sys

# This is Django-Environ, not environ. (!= pip install environ)
import environ
from distutils.util import strtobool


###############################################################################
# 1.a  General Django Configuration
###############################################################################
# Returns the path of this specific python module(<all of this AND>/Rodan/rodan)
# It does not add `settings.py` at the end.
# PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
# Now using Django-Environ instead. We could reorganize the structure of this
# django project to be easier to maintain in the future.
# (Rodan/rodan/settings.py -2 = Rodan/).
# From here, we can specify any path relative to the `ROOT_DIR` of the
# repository by passing folder names to `path`.
# [TODO] - Run tests against this to be absolutely sure it doesn't break.
ROOT_DIR = environ.Path(__file__) - 2
PROJECT_PATH = ROOT_DIR.path("rodan")
# The following variable will move the /admin page in deployment to a random
# link only known to the lab managers/developers. It, along with other env
# variables, must be set prior to installation on the deployment server.
ADMIN_URL = os.getenv("DJANGO_ADMIN_URL")
# Environ.get returns a string, even if it is a bool. You must convert the
# string from environ into a 0 or 1. This can finally be translated into a boolean.
# Python 2.7
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = bool(strtobool(os.environ.get("DJANGO_DEBUG_MODE", "False")))
TEMPLATE_DEBUG = DEBUG
TEST = "test" in sys.argv
TEST_RUNNER = "django.test.runner.DiscoverRunner"
if TEST and not DEBUG:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Testing requires DEBUG=True")
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "America/Montreal"
# Language code for this installation. All choices can be found here:
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# If you set this to False, Django will not use timezone-aware datetimes.
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# Make this unique, and don't share it with anybody.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
# Installed apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "ws4redis",
    "rodan",
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "guardian",
    "corsheaders",
    "sortedm2m",
    # Docker Health Check
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    # [TODO] Make custom checks for these.
    # "health_check.contrib.celery",
    # "health_check.contrib.rabbitmq",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}
# Rodan DATA folder
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.getenv("DJANGO_MEDIA_ROOT")
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
MEDIA_URL = "/uploads/"

###############################################################################
# 1.b  General Rodan Configuration
###############################################################################
# Diva.js support
ENABLE_DIVA = True
# Resource thumbnail
# THUMBNAIL_EXT = "jpg"
# Supported Workflow serialization versions -- see rodan.views.workflow.version_map
RODAN_WORKFLOW_SERIALIZATION_FORMAT_VERSION = 0.1
# 30 days. NULL: never expire
RODAN_RESULTS_PACKAGE_AUTO_EXPIRY_SECONDS = 30 * 24 * 60 * 60
# Default: 15 seconds before the authentication token expires.
RODAN_RUNJOB_WORKING_USER_EXPIRY_SECONDS = 15

###############################################################################
# 1.c  Rodan Job Package Registration
###############################################################################
# Job Packages
RODAN_JOB_QUEUE = os.getenv("CELERY_JOB_QUEUE")
RODAN_JOB_PACKAGES = []
BASE_JOB_PACKAGES = [
    "rodan.jobs.resource_distributor",
]
RODAN_PYTHON2_JOBS = [
    #py2 "rodan.jobs.diagonal-neume-slicing",
    #py2 "rodan.jobs.gamera_rodan",
    #py2 "rodan.jobs.helloworld",
    #py2 "rodan.jobs.heuristic-pitch-finding",
    #py2 "rodan.jobs.interactive_classifier",
    #py2 "rodan.jobs.JSOMR2MEI",
    #py2 "rodan.jobs.jSymbolic-Rodan",
    #py2 "rodan.jobs.MEI_encoding",
    #py2 "rodan.jobs.neon-wrapper",
    #py2 "rodan.jobs.pil-rodan",
    #py2 "rodan.jobs.pixel_wrapper",
    #py2 "rodan.jobs.text_alignment",
    #py2 "rodan.jobs.vis-rodan",
]
RODAN_PYTHON3_JOBS = [
    #py3 "rodan.jobs.helloworld",
    #py3 "rodan.jobs.Calvo-classifier",
]

if RODAN_JOB_QUEUE == "None" or RODAN_JOB_QUEUE == "celery":
    # All the jobs must be registered in the database, so all jobs must be here.
    RODAN_JOB_PACKAGES += BASE_JOB_PACKAGES
    RODAN_JOB_PACKAGES += RODAN_PYTHON2_JOBS
    RODAN_JOB_PACKAGES += RODAN_PYTHON3_JOBS
elif RODAN_JOB_QUEUE == "Python2":
    RODAN_JOB_PACKAGES += BASE_JOB_PACKAGES
    RODAN_JOB_PACKAGES += RODAN_PYTHON2_JOBS
elif RODAN_JOB_QUEUE == "Python3":
    RODAN_JOB_PACKAGES += BASE_JOB_PACKAGES
    RODAN_JOB_PACKAGES += RODAN_PYTHON3_JOBS
else:
    raise EnvironmentError(
        "An environment was not built for that specific rodan job-queue yet. " +
        "Build one and try again."
    )

# Jobs that depend on binaries.
# If None, Rodan will call `which gm` to find it.
BIN_GM = "/usr/bin/gm"
# If None, Rodan will call `which kdu_compress` to find it.
BIN_KDU_COMPRESS = "/vendor/kakadu_v7_6/bin/Linux-x86-64-gcc/kdu_compress"
# If None, Rodan will call `which vips` to find it.
BIN_VIPS = "/usr/bin/vips"
# If None, Rodan will call `which xmllint` to find it.
BIN_XMLLINT = "/usr/bin/xmllint"


###############################################################################
# 1.d  Logging configuration (rodan.log, database.log)
###############################################################################
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/code/Rodan/rodan.log",
            "formatter": "verbose",
        },
        "dblog": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/code/Rodan/database.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
        # When you set the logging for django to DEBUG, you get lots of extra noise
        # Use level "DEBUG" only if you really have to.
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": True},
        # Rodan errors should be more noisy though.
        "rodan": {"handlers": ["file"], "level": "DEBUG", "propagate": True},
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["dblog"],
            "propagate": False,
        },
    },
}


###############################################################################
# 1.e  Email configuration
###############################################################################
# A sample email configuration. These parameters are used to send emails to
# the owner of WorkflowRuns, etc.
# To enable emailing, fill out email parameters below and set EMAIL_USE to True.
# See https://docs.djangoproject.com/en/1.10/topics/email/ for
# more details on how to customize your email configuration.

# [TODO] - Setup proper email configuration.

# EMAIL_USE = True
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASS')
# EMAIL_PORT = 587


###############################################################################
# 2.a  Rodan Server Configuration
###############################################################################
# Django entrance
ROOT_URLCONF = "rodan.urls"
# let Django know if the request is HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_SCHEME", "https")
# Allowed hosts
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS").split(",")
SESSION_COOKIE_SECURE = os.getenv("SSL_COOKIE")
SESSION_COOKIE_DOMAIN = os.getenv("SSL_COOKIE_DOMAIN")
# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = [
#     "django.template.loaders.filesystem.Loader",
#     "django.template.loaders.app_directories.Loader",
#     # 'django.template.loaders.eggs.Loader',
# ]
# TEMPLATE_DIRS = [
#     # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
# ]
# TEMPLATE_CONTEXT_PROCESSORS = [
#     "django.contrib.auth.context_processors.auth",
#     "django.core.context_processors.debug",
#     "django.core.context_processors.media",
#     "django.core.context_processors.static",
#     "django.core.context_processors.csrf",
#     "django.contrib.messages.context_processors.messages",
#     "ws4redis.context_processors.default",
#     # "rodan.context_processors.list_projects",
#     # "rodan.context_processors.login_url",

#     # Default in 1.10
#     # 'django.template.context_processors.debug',
#     # 'django.template.context_processors.request',
#     # 'django.contrib.auth.context_processors.auth',
#     # 'django.contrib.messages.context_processors.messages',
# ]

TEMPLATES = [
    {
        "BACKEND": 'django.template.backends.django.DjangoTemplates',
        "DIRS": [],
        # "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.csrf",
                "django.contrib.messages.context_processors.messages",
                "ws4redis.context_processors.default",
                # "rodan.context_processors.list_projects",
                # "rodan.context_processors.login_url",

                # Default in 1.10
                # 'django.template.context_processors.debug',
                # 'django.template.context_processors.request',
                # 'django.contrib.auth.context_processors.auth',
                # 'django.contrib.messages.context_processors.messages',
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
                # 'django.template.loaders.eggs.Loader',
            ]
        },
    },
]

# Middleware classes
MIDDLEWARE_CLASSES = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # [WIP] Middleware-DEBUG
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
]
FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]
# REST framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication", # [TODO] - Make token auth the only auth.
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_METADATA_CLASS": "rodan.views.RodanMetadata",
    "PAGE_SIZE": 20,
    "MAX_PAGE_SIZE": 100,
    "USE_ABSOLUTE_URLS": True,
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.DjangoObjectPermissionsFilter",
        "rest_framework.filters.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rodan.paginators.pagination.CustomPagination",
}

# used by django-guardian
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # default
    "guardian.backends.ObjectPermissionBackend",
]
# [TODO] This is completely depricated.
# https://django-guardian.readthedocs.io/en/stable/develop/changes.html?highlight=User%20ID#release-1-4-2-mar-09-2016
# Fix it per the suggestions above.
ANONYMOUS_USER_ID = -1

###############################################################################
# 2.b  CORS Configuration
###############################################################################

CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = ('some domain or IP')
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["Set-Cookie", "Vary", "Date"]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

###############################################################################
# 2.c  Websocket configuration
###############################################################################
WEBSOCKET_URL = "/ws/"
WSGI_APPLICATION = "ws4redis.django_runserver.application"
WS4REDIS_CONNECTION = {
    "host": os.getenv("REDIS_HOST"),
    "port": os.getenv("REDIS_PORT"),
    "db": os.getenv("REDIS_DB"),
}
WS4REDIS_EXPIRE = 3600
WS4REDIS_HEARTBEAT = "--heartbeat--"
WS4REDIS_PREFIX = "rodan"

###############################################################################
# 2.d  IIPServer Configuration (if using Diva.js)
###############################################################################
# IIP Server URL
IIPSRV_URL = os.getenv("IIPSRV_URL")
# IIP Server FILESYSTEM_PREFIX
IIPSRV_FILESYSTEM_PREFIX = os.getenv("DJANGO_MEDIA_ROOT")

###############################################################################
# 2.e  Rodan Development Server Configuration
###############################################################################
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# Additional locations of static files
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(PROJECT_PATH.path("static"))]
# List of finder classes that know how to find static files in
# various locations.
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

###############################################################################
# 3.a  Rodan Worker Configuration
###############################################################################
# Add traceback in RunJob's error detail when it fails.
TRACEBACK_IN_ERROR_DETAIL = True

###############################################################################
# 3.b  Celery Task Queue Configuration
###############################################################################
BROKER_CONNECTION_MAX_RETRIES = "0"
BROKER_URL = os.getenv("RABBITMQ_URL")
CELERY_RESULT_BACKEND = "amqp"
CELERY_ENABLE_UTC = True
CELERY_IMPORTS = ("rodan.jobs.load",)
if TEST:
    # Run Celery task synchronously, instead of sending into queue
    CELERY_ALWAYS_EAGER = True
    # Propagate exceptions in synchronous task running by default
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
# Use temporary filesystem to store projects and resources during test
if TEST:
    import tempfile as _tempfile

    MEDIA_ROOT = _tempfile.mkdtemp() + "/"

###############################################################################
# 3.c  Docker Health Checks
###############################################################################

HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,    # in MB
}
