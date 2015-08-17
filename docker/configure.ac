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
AC_ARG_VAR([RODAN_DATA_DIR], [Rodan data directory (full path)])

# check values
if test -z "$RODAN_DATA_DIR"; then
  AC_MSG_ERROR(RODAN_DATA_DIR missing in arguments)
fi

# always add training slash for directories
length=${#RODAN_DATA_DIR}
last_char=${RODAN_DATA_DIR:length-1:1}
[[ $last_char != "/" ]] && RODAN_DATA_DIR="$RODAN_DATA_DIR/"; :


# substitute variables
AC_SUBST(RODAN_DATA_DIR)


# Database
AC_ARG_VAR([DB_NAME], [Database name (default rodan)])
AC_ARG_VAR([DB_USER], [Database user (default rodan)])
AC_ARG_VAR([DB_PASSWORD], [Database password])
AC_ARG_VAR([DB_HOST], [Database host (default localhost)])

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

AC_SUBST(DB_NAME)
AC_SUBST(DB_USER)
AC_SUBST(DB_PASSWORD)
AC_SUBST(DB_HOST)
AC_SUBST(DB_PORT)

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


# output
AC_CONFIG_FILES(Dockerfile deploy.sh)
AC_OUTPUT()
