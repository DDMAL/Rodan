# Process this file with autoconf to produce a configure script
AC_INIT(Rodan Dockerfile,0.01)
AC_COPYRIGHT(Copyright 2011-2015 Distributed Digital Music Archives and Libraries Lab)


# Check features
# diva.js (default enable)
AC_ARG_ENABLE([diva],
        AS_HELP_STRING([--disable-diva], [disable Diva.js]))

if test "x$enable_diva" != "xno"; then
  CONFIGURE_DIVA="--enable-diva"
  IF_DIVA=""
else
  CONFIGURE_DIVA="--disable-diva"
  IF_DIVA='# '
fi

# substitute variables
AC_SUBST(CONFIGURE_DIVA)
AC_SUBST(IF_DIVA)



# MODE: server or worker
AC_ARG_VAR([MODE], [Automated setup mode: server | worker])

# check values
if test "x$MODE" = "xserver"; then
   IF_SERVER=""
elif test "x$MODE" = "xworker"; then
   IF_SERVER='# '
else
  AC_MSG_ERROR(MODE must be either server or worker)
fi

AC_SUBST(MODE)
AC_SUBST(IF_SERVER)



# Set directories
AC_ARG_VAR([RODAN_DATA_DIR], [Shared Rodan data directory (full path, required when MODE=server)])

# check values
if test "x$MODE" = "xserver"; then
  if test -z "$RODAN_DATA_DIR"; then
    AC_MSG_ERROR(RODAN_DATA_DIR required when MODE=server)
  fi

  # always add training slash for directories
  length=${#RODAN_DATA_DIR}
  last_char=${RODAN_DATA_DIR:length-1:1}
  [[ $last_char != "/" ]] && RODAN_DATA_DIR="$RODAN_DATA_DIR/"; :
fi

# substitute variables
AC_SUBST(RODAN_DATA_DIR)


# Database
AC_ARG_VAR([DB_NAME], [Database name (default rodan)])
AC_ARG_VAR([DB_USER], [Database user (default rodan)])
AC_ARG_VAR([DB_PASSWORD], [Database password])
AC_ARG_VAR([DB_HOST], [Database host (default localhost)])
AC_ARG_VAR([DB_PORT], [Database port (default 5432)])
AC_ARG_VAR([WORKERS_SUBNET], [Workers subnet (only MODE=server)])
AC_ARG_VAR([SERVER_IP], [Server IP (only MODE=worker)])


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
if test -z "$WORKERS_SUBNET"; then
  if test "x$MODE" = "xserver"; then
    AC_MSG_ERROR([WORKERS_SUBNET required when MODE=server (e.g. 192.168.1.0/24)])
  fi
fi
if test -z "$SERVER_IP"; then
  if test "x$MODE" = "xworker"; then
    AC_MSG_ERROR([SERVER_IP required when MODE=worker (e.g. 192.168.1.2)])
  fi
fi


AC_SUBST(DB_NAME)
AC_SUBST(DB_USER)
AC_SUBST(DB_PASSWORD)
AC_SUBST(DB_HOST)
AC_SUBST(DB_PORT)
AC_SUBST(WORKERS_SUBNET)
AC_SUBST(SERVER_IP)

# Redis
if test "x$MODE" = "xserver"; then
   REDIS_HOST="localhost"
elif test "x$MODE" = "xworker"; then
   REDIS_HOST="$SERVER_IP"
fi
AC_SUBST(REDIS_HOST)

# admin account (only MODE=server)
AC_ARG_VAR([ADMIN_USER], [Admin user name (default admin, only MODE=server)])
AC_ARG_VAR([ADMIN_PASSWORD], [Admin user password (default admin, only MODE=server)])
if test -z "$ADMIN_USER"; then
  AC_MSG_WARN(set default: ADMIN_USER=admin)
  ADMIN_USER=admin
fi
if test -z "$ADMIN_PASSWORD"; then
  AC_MSG_WARN(set default: ADMIN_PASSWORD=admin)
  ADMIN_PASSWORD=admin
fi

AC_SUBST(ADMIN_USER)
AC_SUBST(ADMIN_PASSWORD)



# Celery broker (only MODE=worker)
AC_ARG_VAR([CELERY_BROKER_URL], [Celery broker URL (only MODE=worker)])

if test "x$MODE" = "xserver"; then
  CELERY_BROKER_URL=amqp://rodanuser:DDMALrodan@localhost:5672/DDMAL
else
  if test -z "$CELERY_BROKER_URL"; then
    AC_MSG_ERROR(CELERY_BROKER_URL required when MODE=worker)
  fi
fi

AC_SUBST(CELERY_BROKER_URL)


# Domain name (only MODE=server)
AC_ARG_VAR([DOMAIN_NAME], [Domain name (only MODE=server)])

if test "x$MODE" = "xserver"; then
  if test -z "$DOMAIN_NAME"; then
    AC_MSG_ERROR(DOMAIN_NAME missing in arguments)
  fi
fi

AC_SUBST(DOMAIN_NAME)


# Client max body size (only MODE=server)
AC_ARG_VAR([CLIENT_MAX_BODY_SIZE], [Max size of HTTP request, related to the size of resource file (default 20M, only MODE=server)])
if test "x$MODE" = "xserver"; then
  if test -z "$CLIENT_MAX_BODY_SIZE"; then
    AC_MSG_WARN([set default: CLIENT_MAX_BODY_SIZE=20M])
    CLIENT_MAX_BODY_SIZE=20M
  fi
fi

AC_SUBST(CLIENT_MAX_BODY_SIZE)


# Rodan data folder mount point (only MODE=server)
AC_ARG_VAR([RODAN_DATA_DIR], [Mount point of Rodan data directory (only MODE=server)])
if test "x$MODE" = "xserver"; then
  if test -z "$RODAN_DATA_DIR"; then
    AC_MSG_ERROR([RODAN_DATA_DIR required when MODE=server])
  fi
fi

AC_SUBST(RODAN_DATA_DIR)


# output
AC_CONFIG_FILES(Dockerfile deploy.sh)
AC_OUTPUT()
