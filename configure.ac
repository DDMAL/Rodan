# Process this file with autoconf to produce a configure script
AC_INIT(Rodan,1.0.0)
AC_COPYRIGHT(Copyright 2011-2015 Distributed Digital Music Archives and Libraries Lab)


# Check features
# debug (default disable)
AC_ARG_ENABLE([debug],
        AS_HELP_STRING([--enable-debug], [enable debug mode]))
if test "x$enable_debug" = "xyes"; then
   ENABLE_DEBUG=True
   AC_MSG_NOTICE([DEBUG mode is on.])
else
   ENABLE_DEBUG=False
   AC_MSG_NOTICE([DEBUG mode is off.])
fi

# diva.js (default enable)
AC_ARG_ENABLE([diva],
        AS_HELP_STRING([--disable-diva], [disable Diva.js]))
if test "x$enable_diva" != "xno"; then
   ENABLE_DIVA=True
   IF_DIVA=""
   AC_MSG_NOTICE([Diva.js is enabled.])
else
   ENABLE_DIVA=False
   IF_DIVA="# "
   DIVA_JPEG2000_CONVERTER=None
   DIVA_JPEG2000_CONVERTER_INPUT=None
   DIVA_JPEG2000_CONVERTER_OUTPUT=None
   AC_MSG_NOTICE([Diva.js is disabled.])
fi

# substitute variables
AC_SUBST(ENABLE_DEBUG)
AC_SUBST(ENABLE_DIVA)
AC_SUBST(IF_DIVA)
AC_SUBST(DIVA_JPEG2000_CONVERTER)
AC_SUBST(DIVA_JPEG2000_CONVERTER_INPUT)
AC_SUBST(DIVA_JPEG2000_CONVERTER_OUTPUT)


# MODE: server or worker
AC_ARG_VAR([MODE], [Rodan source code configure mode: server | worker])

# check values
if test "x$MODE" = "xserver"; then
   IF_SERVER=""
   AC_MSG_NOTICE([Rodan source code will be configured as "server".])
elif test "x$MODE" = "xworker"; then
   IF_SERVER='# '
   AC_MSG_NOTICE([Rodan source code will be configured as "worker".])
else
   AC_MSG_ERROR(MODE must be either server or worker)
fi

AC_SUBST(IF_SERVER)


# Checks for programs for jobs
# graphicsmagick
AC_ARG_WITH(graphicsmagick-search-path,
                AS_HELP_STRING([--with-graphicsmagick-search-path],[specify the additional graphicsmagick search path]),
                [graphicsmagick_search_path=$withval])

AC_PATH_PROG([BIN_GM], [gm], [:], [${graphicsmagick_search_path}:$PATH])
if test ! -f "$BIN_GM"; then
        AS_IF([test "x$ENABLE_DIVA" = "xTrue"], [AC_MSG_ERROR(Can't find graphicsmagick for Diva.js)], [AC_MSG_WARN([Can't find graphicsmagick. Some optical music recognition jobs will not function.])])
        BIN_GM=None               # Python None
else
        BIN_GM="'$BIN_GM'"        # Python string
fi

# kdu_compress (if with diva)
AC_ARG_WITH(kdu_compress-search-path,
                AS_HELP_STRING([--with-kdu_compress-search-path],[specify the additional kdu_compress search path]),
                [kdu_compress_search_path=$withval])

AC_PATH_PROG([BIN_KDU_COMPRESS], [kdu_compress], [:], [${kdu_compress_search_path}:$PATH])

if test ! -f "$BIN_KDU_COMPRESS"; then
        AS_IF([test "x$ENABLE_DIVA" = "xTrue"], [AC_MSG_ERROR(Can't find kdu_compress for Diva.js)], [AC_MSG_WARN([Can't find kdu_compress. Some optical music recognition jobs will not function.])])
        BIN_KDU_COMPRESS=None                    # Python None
else
        BIN_KDU_COMPRESS="'$BIN_KDU_COMPRESS'"   # Python string
fi

# xmllint
AC_ARG_WITH(xmllint-search-path,
                AS_HELP_STRING([--with-xmllint-search-path],[specify the additional xmllint search path]),
                [xmllint_search_path=$withval])

AC_PATH_PROG([BIN_XMLLINT], [xmllint], [:], [${xmllint_search_path}:$PATH])

if test ! -f "$BIN_XMLLINT"; then
        AC_MSG_WARN(Can't find xmllint. Some optical music recognition jobs will not function.)
        BIN_XMLLINT=None                  # Python None
else
        BIN_XMLLINT="'$BIN_XMLLINT'"      # Python string
fi

# vips
AC_ARG_WITH(vips-search-path,
                AS_HELP_STRING([--with-vips-search-path],[specify the additional vips search path]),
                [vips_search_path=$withval])

AC_PATH_PROG([BIN_VIPS], [vips], [:], [${vips_search_path}:$PATH])

if test ! -f "$BIN_VIPS"; then
        AC_MSG_WARN(Can't find vips. Some optical music recognition jobs will not function.)
        BIN_VIPS=None               # Python None
else
        BIN_VIPS="'$BIN_VIPS'"   # Python string
fi

# substitute variables
AC_SUBST(BIN_GM)
AC_SUBST(BIN_KDU_COMPRESS)
AC_SUBST(BIN_XMLLINT)
AC_SUBST(BIN_VIPS)



# Set directories
RODAN_APP_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
AC_MSG_NOTICE([Rodan source code directory: $RODAN_APP_DIR])

AC_ARG_VAR([RODAN_VENV_DIR], [Virtual environment directory (full path)])
AC_ARG_VAR([RODAN_DATA_DIR], [Rodan data directory (full path)])

# check values
if test -z "$RODAN_VENV_DIR"; then
  AC_MSG_ERROR(RODAN_VENV_DIR missing in arguments)
else
  if test ! -d "$RODAN_VENV_DIR"; then
    AC_MSG_ERROR(RODAN_VENV_DIR doesn't exist)
  fi
fi

if test -z "$RODAN_DATA_DIR"; then
  AC_MSG_ERROR(RODAN_DATA_DIR missing in arguments)
else
  if test ! -d "$RODAN_DATA_DIR"; then
    AC_MSG_ERROR(RODAN_DATA_DIR doesn't exist)
  fi
fi

# always add training slash for directories
length=${#RODAN_APP_DIR}
last_char=${RODAN_APP_DIR:length-1:1}
[[ $last_char != "/" ]] && RODAN_APP_DIR="$RODAN_APP_DIR/"; :

length=${#RODAN_VENV_DIR}
last_char=${RODAN_VENV_DIR:length-1:1}
[[ $last_char != "/" ]] && RODAN_VENV_DIR="$RODAN_VENV_DIR/"; :

length=${#RODAN_DATA_DIR}
last_char=${RODAN_DATA_DIR:length-1:1}
[[ $last_char != "/" ]] && RODAN_DATA_DIR="$RODAN_DATA_DIR/"; :


# substitute variables
AC_SUBST(RODAN_APP_DIR)
AC_SUBST(RODAN_VENV_DIR)
AC_SUBST(RODAN_DATA_DIR)


# Secret Key
AC_ARG_VAR([SECRET_KEY], [Secret key for encrypting credentials (required)])
if test -z "$SECRET_KEY"; then
  AC_MSG_ERROR(SECRET_KEY missing in arguments)
fi


# Database
AC_ARG_VAR([DB_NAME], [Database name (default rodan)])
AC_ARG_VAR([DB_USER], [Database user (default rodan)])
AC_ARG_VAR([DB_PASSWORD], [Database password])
AC_ARG_VAR([DB_HOST], [Database host (default localhost)])
AC_ARG_VAR([DB_PORT], [Database port (default 5432)])
AC_ARG_VAR([DB_USER_TEST], [Database user (default the same as DB_USER)])
AC_ARG_VAR([DB_PASSWORD_TEST], [Database password (default the same as DB_USER)])

if test -z "$DB_NAME"; then
  AC_MSG_WARN(set default: DB_NAME=rodan)
  DB_NAME=rodan
fi
if test -z "$DB_USER"; then
  AC_MSG_WARN(set default: DB_USER=rodan)
  DB_USER=rodan
fi
if test -z "$DB_PASSWORD"; then
  AC_MSG_ERROR(DB_PASSWORD missing in arguments)
fi
if test -z "$DB_HOST"; then
  AC_MSG_WARN(set default: DB_HOST=localhost)
  DB_HOST=localhost
fi
if test -z "$DB_PORT"; then
  AC_MSG_WARN(set default: DB_PORT=5432)
  DB_PORT=5432
fi
if test -z "$DB_USER_TEST"; then
  AC_MSG_WARN([set default: DB_USER_TEST=$DB_USER])
  DB_USER_TEST="$DB_USER"
fi
if test -z "$DB_PASSWORD_TEST"; then
  AC_MSG_WARN([set default: DB_PASSWORD_TEST=$DB_PASSWORD])
  DB_PASSWORD_TEST="$DB_PASSWORD"
fi

# Redis
AC_ARG_VAR([REDIS_HOST], [Redis host (default localhost)])
AC_ARG_VAR([REDIS_PORT], [Redis port (default 6379)])
AC_ARG_VAR([REDIS_DB], [Redis database number (default 0)])

if test -z "$REDIS_HOST"; then
  AC_MSG_WARN(set default: REDIS_HOST=localhost)
  REDIS_HOST=localhost
fi
if test -z "$REDIS_PORT"; then
  AC_MSG_WARN(set default: REDIS_PORT=6379)
  REDIS_PORT=6379
fi
if test -z "$REDIS_DB"; then
  AC_MSG_WARN(set default: REDIS_DB=0)
  REDIS_DB=0
fi



# RabbitMQ
AC_ARG_VAR([AMQP_HOST], [RabbitMQ host (default localhost)])
AC_ARG_VAR([AMQP_PORT], [RabbitMQ port (default 5672)])
AC_ARG_VAR([AMQP_VHOST], [RabbitMQ vhost name (default rodan)])
AC_ARG_VAR([AMQP_USER], [RabbitMQ user (default rodan)])
AC_ARG_VAR([AMQP_PASSWORD], [RabbitMQ password])

if test -z "$AMQP_HOST"; then
  AC_MSG_WARN(set default: AMQP_HOST=localhost)
  AMQP_HOST=localhost
fi
if test -z "$AMQP_PORT"; then
  AC_MSG_WARN(set default: AMQP_PORT=5672)
  AMQP_PORT=5672
fi
if test -z "$AMQP_VHOST"; then
  AC_MSG_WARN(set default: AMQP_VHOST=rodan)
  AMQP_VHOST=rodan
fi
if test -z "$AMQP_USER"; then
  AC_MSG_WARN(set default: AMQP_USER=rodan)
  AMQP_USER=rodan
fi
if test -z "$AMQP_PASSWORD"; then
  AC_MSG_ERROR(AMQP_PASSWORD missing in arguments)
fi

CELERY_BROKER_URL=amqp://$AMQP_USER:$AMQP_PASSWORD@$AMQP_HOST:$AMQP_PORT/$AMQP_VHOST



# Domain name (only MODE=server)
AC_ARG_VAR([DOMAIN_NAME], [Domain name (required if MODE=server)])

if test "x$MODE" = "xserver"; then
  if test -z "$DOMAIN_NAME"; then
    AC_MSG_ERROR(DOMAIN_NAME missing in arguments)
  fi
else
  DOMAIN_NAME="rodan-worker"
fi

# Paginate by (only MODE=server)
AC_ARG_VAR([PAGINATE_BY], [Paginate by ? items (default=20, required if MODE=server)])
if test "x$MODE" = "xserver"; then
  if test -z "$PAGINATE_BY"; then
    AC_MSG_WARN([set default: PAGINATE_BY=20])
    PAGINATE_BY=20
  fi
else
  PAGINATE_BY=0 # dummy value for workers
fi

# Client max body size (only MODE=server)
AC_ARG_VAR([CLIENT_MAX_BODY_SIZE], [Max size of HTTP request, related to the size of resource file (default 20M, required if MODE=server)])
if test "x$MODE" = "xserver"; then
  if test -z "$CLIENT_MAX_BODY_SIZE"; then
    AC_MSG_WARN([set default: CLIENT_MAX_BODY_SIZE=20M])
    CLIENT_MAX_BODY_SIZE=20M
  fi
fi

# SSL certificate (only MODE=server)
AC_ARG_VAR([SSL_CERT], [Path to SSL certificate file (required if MODE=server)])
AC_ARG_VAR([SSL_CERT_KEY], [Path to SSL certificate key file (required if MODE=server)])
if test "x$MODE" = "xserver"; then
  if test -z "$SSL_CERT"; then
    AC_MSG_ERROR(SSL_CERT missing in arguments)
  fi
  if test ! -f "$SSL_CERT"; then
    AC_MSG_ERROR([SSL_CERT file not found])
  fi
  if test -z "$SSL_CERT_KEY"; then
    AC_MSG_ERROR(SSL_CERT_KEY missing in arguments)
  fi
  if test ! -f "$SSL_CERT_KEY"; then
    AC_MSG_ERROR([SSL_CERT_KEY file not found])
  fi
fi



# substitute variables
AC_SUBST(SECRET_KEY)
AC_SUBST(DB_NAME)
AC_SUBST(DB_USER)
AC_SUBST(DB_PASSWORD)
AC_SUBST(DB_HOST)
AC_SUBST(DB_PORT)
AC_SUBST(REDIS_HOST)
AC_SUBST(REDIS_PORT)
AC_SUBST(REDIS_DB)
AC_SUBST(CELERY_BROKER_URL)
AC_SUBST(DOMAIN_NAME)
AC_SUBST(PAGINATE_BY)
AC_SUBST(CLIENT_MAX_BODY_SIZE)
AC_SUBST(SSL_CERT)
AC_SUBST(SSL_CERT_KEY)
AC_SUBST(EMAIL_USERNAME)
AC_SUBST(EMAIL_PASSWORD)
AC_SUBST(MAX_PAGINATE_BY)

# IIPServer bin
AC_ARG_VAR([IIPSRV_FCGI], [IIPServer fcgi binary (required if --enable-diva and MODE=server)])

if test "x$MODE" = "xserver"; then
  if test "x$ENABLE_DIVA" = "xTrue"; then
    if test -z "$IIPSRV_FCGI"; then
      AC_MSG_ERROR([IIPSRV_FCGI required when --enable-diva=yes])
    fi
    if test ! -f "$IIPSRV_FCGI"; then
      AC_MSG_ERROR([IIPSRV_FCGI fcgi binary not found])
    fi
  fi
fi
if test -z "$IIPSRV_FCGI"; then
  IIPSRV_FCGI=N/A
fi

# User and Group that runs Rodan
AC_ARG_VAR([WWW_USER], [The user to run as (default: www-data)])
AC_ARG_VAR([WWW_GROUP], [The group to run as (default: www-data)])
if test -z "$WWW_USER"; then
  AC_MSG_WARN(set default: WWW_USER=www-data)
  WWW_USER=www-data
fi
if test -z "$WWW_GROUP"; then
  AC_MSG_WARN(set default: WWW_GROUP=www-data)
  WWW_GROUP=www-data
fi


# output
AC_CONFIG_FILES(celery_start.sh rodan/settings.py etc/supervisor/conf.d/rodan.conf)
if test "x$MODE" = "xserver"; then
  AC_CONFIG_FILES(gunicorn_start.sh websocket_start.sh  etc/nginx/sites-available/rodan)
fi

AC_OUTPUT()

# set permissions
chmod a+x celery_start.sh
touch rodan.log
touch database.log
chmod g+w rodan.log database.log

if test "x$MODE" = "xserver"; then
  chmod a+x gunicorn_start.sh websocket_start.sh
fi

AC_MSG_NOTICE([Please run: sudo chgrp -R $WWW_GROUP *; sudo chown -R $WWW_USER:$WWW_GROUP $RODAN_DATA_DIR])
