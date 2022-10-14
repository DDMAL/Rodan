FROM alpine:3 AS builder
ARG BRANCH
ENV BRANCH="${BRANCH:-develop}"
RUN apk update
RUN apk add \
  bash \
  git \
  npm \
  python3 \
  yarn

# Build Pixel
RUN git clone --recurse-submodules -b v2.0.1 https://github.com/DDMAL/pixel_wrapper.git
WORKDIR /pixel_wrapper/
RUN python3 activate_wrapper.py
RUN npm install
RUN ./node_modules/.bin/gulp develop:rodan

# Build Neon
WORKDIR /
RUN git clone --recurse-submodules -b "${BRANCH}" https://github.com/DDMAL/neon_wrapper
WORKDIR /neon_wrapper
RUN git submodule update --init
RUN git submodule update --remote
RUN yarn install
RUN yarn build

# Make Gamera files accessible to the main container.
FROM ddmal/gamera4:v1.0.1 AS gamera

# This release is based on Debian 11 "Bullseye"
FROM python:3.7-slim

# Copy various scripts and make them executable.
# COPY ./scripts/start-celery /run/
# COPY ./scripts/wait-for-app /run/
# RUN chmod +x /run/start-celery
# RUN chmod +x /run/wait-for-app

# Copy external dependencies into main container.
# rodan-main is not pulled from builder (to ease local development)
COPY ./rodan-main/code /code/Rodan
COPY --from=builder /pixel_wrapper /code/Rodan/rodan/jobs/pixel_wrapper
COPY --from=builder /neon_wrapper /code/Rodan/rodan/jobs/neon_wrapper
# Gamera and Musicstaves will be installed later in this script.
COPY --from=gamera /gamera4-rodan /gamera4-rodan

# Install dependencies.
RUN apt-get update
RUN apt-get install -y \
  bash \
  curl \
  g++ \
  git \
  # python-magic dependency
  libmagic1 \
  # Psycopg2 dependency
  libpq-dev \
  # OpenCV dependencies
  libsm6 libxext6 libxrender-dev libglib2.0-data \
  python3-opencv \
  wget \
  vim

# https://stackoverflow.com/questions/69100275/error-while-downloading-the-requirements-using-pip-install-setup-command-use-2
RUN pip3 install setuptools==58
RUN pip3 install -r /code/Rodan/requirements.txt

# Install Gamera and Musicstaves.
WORKDIR /gamera4-rodan/gamera-4
RUN python3 setup.py --nowx install
WORKDIR /gamera4-rodan/musicstaves
RUN python3 setup.py install

# Temporary fix for OpenCV until https://github.com/DDMAL/Rodan/issues/639 is resolved.
RUN pip install opencv-python==4.6.0.66

# ====================
# Rodan-main container
# ====================
#FROM python:3.7-slim

#COPY ./rodan-main/code /code/Rodan

# Install postgres
#RUN apt update \
#  # && apt-get install -y postgresql-plpython-${PG_MAJOR} python-pip \
#  && apt install -y postgresql-plpython3-11 \
#  && rm -rf /var/lib/apt/lists/*

# Install dependencies.
RUN apt-get update
RUN apt-get install -y \
  bash \
  curl \
  g++ \
  git \
  # python-magic dependency
  libmagic1 \
  # Psycopg2 dependency
  libpq-dev \
  # OpenCV dependencies
  libsm6 libxext6 libxrender-dev libglib2.0-data \
  python3-opencv \
  wget \
  vim \
  sudo \
  postgresql

# https://stackoverflow.com/questions/69100275/error-while-downloading-the-requirements-using-pip-install-setup-command-use-2
RUN pip3 install setuptools==58
RUN pip3 install -r /code/Rodan/requirements.txt

# Temporary fix for OpenCV until https://github.com/DDMAL/Rodan/issues/639 is resolved.
RUN pip install opencv-python==4.6.0.66

# From rodan-main
RUN set -x \
    && mkdir /vendor || echo "Already exists" \
    && apt update \
    && apt -q install -y \
    libopenjp2-7 \
    libopenjp2-7-dev \
    libopenjp2-tools

# We need make to compile Grok.
RUN apt-get install -y make

# Install Grok
RUN cd /vendor \
  && wget --no-check-certificate -qO - https://cmake.org/files/v3.17/cmake-3.17.0-Linux-x86_64.tar.gz | tar -xzf - \
  && /vendor/cmake-3.17.0-Linux-x86_64/bin/cmake --help \
  && git clone https://github.com/raviraina/grok.git \
  && cd grok \
  # && git checkout 2203be8 \
  && git checkout 4932d86b19d9008a28ae898035cfa43340e636e6 \
  && mkdir build \
  && cd build \
  && /vendor/cmake-3.17.0-Linux-x86_64/bin/cmake -DBUILD_THIRDPARTY=ON ..  \
  && make -j3

# Copy script to start postgres
COPY ./ci-jobs/prepare-ci.bash /run/

# Environemtn Variables
ENV CELERY_JOB_QUEUE=None

ENV ADMIN_USER=rodan
ENV ADMIN_PASS=rodan
ENV DJANGO_DEBUG_MODE=False
ENV DJANGO_SECRET_KEY=localdev
ENV DJANGO_MEDIA_ROOT=/rodan/data/
ENV DJANGO_ALLOWED_HOSTS="*"
ENV DJANGO_ADMIN_URL=admin/
ENV IIPSRV_URL=http://localhost/fcgi-bin/iipsrv.fcgi/
ENV DJANGO_ACCESS_LOG=/code/Rodan/rodan.log
ENV DJANGO_DEBUG_LOG=/code/Rodan/database.log
ENV SERVER_HOST=""

ENV C_FORCE_ROOT=true

ENV POSTGRES_HOST=127.0.0.1
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=rodan
ENV POSTGRES_USER=rodan
ENV POSTGRES_PASSWORD=rodan
ENV POSTGRES_DATABASE_LOGFILE=/code/Rodan/database.log

ENV RABBITMQ_URL=amqp://guest_user:guest_pass@rabbitmq:5672//
ENV RABBITMQ_DEFAULT_USER=guest_user
ENV RABBITMQ_DEFAULT_PASS=guest_pass

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_DB=0