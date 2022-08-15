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
RUN git clone --recurse-submodules -b "${BRANCH}" https://github.com/DDMAL/pixel_wrapper.git
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

# Build Rodan
WORKDIR /
RUN git clone --recurse-submodules -b "${BRANCH}" https://github.com/ddmal/Rodan

# Make Gamera files accessible to the main container.
FROM ddmal/gamera4 AS gamera

# Ubuntu 20.04 is an LTS release, supported until April 2025.
FROM ubuntu:20.04

# Copy various scripts and make them executable.
COPY ./scripts/start-celery /run/
COPY ./scripts/wait-for-app /run/
RUN chmod +x /run/start-celery
RUN chmod +x /run/wait-for-app

# Copy external dependencies into main container.
# Rodan folder MUST be uppercase, otherwise many unittests fail.
COPY --from=builder /Rodan/rodan-main/code /code/Rodan
COPY --from=builder /pixel_wrapper /code/Rodan/rodan/jobs/
COPY --from=builder /neon_wrapper /code/Rodan/rodan/jobs/
# Gamera and Musicstaves will be installed later in this script.
COPY --from=gamera /gamera4-rodan /gamera4-rodan

# Install tools and dependencies.
RUN apt-get update
# Skip setting the timezone. https://stackoverflow.com/questions/44331836/apt-get-install-tzdata-noninteractive
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN apt-get install -y \
  bash \
  curl \
  git \
  python3.8 \
  python3-lxml \
  python3-numpy \
  python3-opencv \
  python3-pika \
  python3-pil \
  python3-pip \
  wget \
  vim \
  # Psycopg2 dependency
  libpq-dev

# Installing wheel makes the rest of the installation faster.
# https://stackoverflow.com/questions/69100275/error-while-downloading-the-requirements-using-pip-install-setup-command-use-2
RUN pip3 install setuptools==58 wheel
RUN pip3 install -r /code/Rodan/requirements.txt

# Install Gamera and Musicstaves.
WORKDIR /gamera4-rodan/gamera-4
RUN python3 setup.py --nowx install
WORKDIR /gamera4-rodan/musicstaves
RUN python3 setup.py install

# Change the concurency for python3 jobs (Calvo)
RUN sed -i "s/=10/=1/g" /run/start-celery

ENTRYPOINT ["/run/start-celery"]
