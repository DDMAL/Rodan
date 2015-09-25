from settings_production import *
import os

TEMPLATE_DEBUG = DEBUG
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Montreal'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'v(07vo4vp0y-)rm1u*udkd-#vuc2ln@v&amp;u3t4rg)ze1f!9+)uo'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

if DEBUG:
    # we avoid unnecessary middlewares in production as they slows down the website.
    # for DEBUG mode, we would like to have Django admin which requires Session and Message.
    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES) + [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware'
    ]

ROOT_URLCONF = 'rodan.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# CELERYCAM_EXPIRE_SUCCESS = timedelta(days=30)
# CELERYCAM_EXPIRE_SUCCESS = None
# CELERYCAM_EXPIRE_ERROR = None
# CELERYCAM_EXPIRE_PENDING = None

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'ws4redis',
    'rodan',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'guardian',
    'corsheaders',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'rodan.log',
            'formatter': 'verbose'
        },
        'dblog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'database.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            #'level': 'DEBUG',
            'propagate': True,
        },
        'rodan': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['dblog'],
            'propagate': False,
        }
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.csrf",
    "django.contrib.messages.context_processors.messages",
    'ws4redis.context_processors.default',
    # "rodan.context_processors.list_projects",
    # "rodan.context_processors.login_url",
)

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_METADATA_CLASS': 'rodan.views.RodanMetadata',
    'PAGINATE_BY': 20,
    'USE_ABSOLUTE_URLS': True,
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',
                                'rest_framework.filters.OrderingFilter')
}
if DEBUG:
    # Enable browsable API
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
    )
    # Enable basic authentication to browse the API
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )

# used by django-guardian
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # default
    'guardian.backends.ObjectPermissionBackend',
)

# used by django-guardian, as django-guardian supports anonymous user object permissions
# `python manage.py syncdb` will create a User instance for the anonymous user with name AnonymousUser
ANONYMOUS_USER_ID = -1

# So that calling get_profile on a user will return the RodanUser instance
# AUTH_PROFILE_MODULE = 'rodan.RodanUser'

THUMBNAIL_EXT = 'jpg'
SMALL_THUMBNAIL = 150
MEDIUM_THUMBNAIL = 400
LARGE_THUMBNAIL = 1500
THUMBNAIL_SIZES = (SMALL_THUMBNAIL, MEDIUM_THUMBNAIL, LARGE_THUMBNAIL)

# Supported Workflow serialization versions -- see rodan.views.workflow.version_map
RODAN_WORKFLOW_SERIALIZATION_FORMAT_VERSION = 0.1

RODAN_RESULTS_PACKAGE_AUTO_EXPIRY_SECONDS = 30 * 24 * 60 * 60  # 30 days. NULL: never expire

# Add traceback in RunJob's error detail when it fails.
TRACEBACK_IN_ERROR_DETAIL = True



###############################################################################
## Celery configuration
###############################################################################
CELERY_ENABLE_UTC = True
CELERY_IMPORTS = ("rodan.jobs.load",)
import sys as _sys
TEST = 'test' in _sys.argv
if TEST:
    CELERY_ALWAYS_EAGER=True  # Run Celery task synchronously, instead of sending into queue
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True  # Propagate exceptions in synchronous task running by default


# Use temporary filesystem to store projects and resources during test
if TEST:
    import tempfile as _tempfile
    MEDIA_ROOT = _tempfile.mkdtemp() + '/'

if TEST and not DEBUG:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Testing requires DEBUG=True")

#######################
## Websocket configuration
#######################
WEBSOCKET_URL = '/ws/'
WSGI_APPLICATION = 'ws4redis.django_runserver.application'
WS4REDIS_EXPIRE = 3600
WS4REDIS_HEARTBEAT = '--heartbeat--'
WS4REDIS_PREFIX = 'rodan'
