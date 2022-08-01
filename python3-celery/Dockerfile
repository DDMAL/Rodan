FROM alpine:3 AS pixel
RUN apk update
RUN apk add \
  git \
  npm \
  python3
RUN git clone --recurse-submodules -b "${BRANCHES:-develop}" https://github.com/DDMAL/pixel_wrapper.git
WORKDIR ./pixel_wrapper/
RUN python3 activate_wrapper.py
RUN npm install
RUN ./node_modules/.bin/gulp develop:rodan


FROM alpine:3 AS neon
RUN apk update
RUN apk add \
  git \
  yarn
# Install Neon
RUN git clone --recurse-submodules -b "${BRANCHES:-develop}" https://github.com/DDMAL/neon_wrapper
WORKDIR ./neon_wrapper
RUN git submodule update --init
RUN git submodule update --remote
RUN yarn install
RUN yarn build

FROM alpine:3
ARG BRANCHES
ARG VERSION

RUN apk update
RUN apk add \
  bash \
  cmake\
  curl \
  ffmpeg \
  g++ \
  git \
  libpng-dev \
  libpq-dev \
  libxml2-dev \
  libxslt-dev \
  nodejs \
  npm \
  py3-gevent \
  py3-lxml \
  py3-markdown \
  py3-matplotlib \
  py3-opencv=4.6.0-r1 \
  py3-pillow \
  py3-pip \
  py3-scipy \
  py3-yaml \
  python3 \
  python3-dev \
  readline \
  tiff-dev \
  uwsgi-python3 \
  vim \
  wget

COPY ./scripts/install_python3_rodan_jobs /run/
COPY ./scripts/start-celery /run/
COPY ./scripts/entrypoint /opt/
COPY ./scripts/wait-for-app /run/

# Copying rodan core from build context into container
# Rodan folder MUST be uppercase, otherwise many unittests fail.
COPY ./rodan-main/code /code/Rodan

# Install Pixel
COPY --from=pixel /pixel_wrapper /code/Rodan/rodan/jobs

# Install Neon
COPY --from=neon /neon_wrapper /code/Rodan/rodan/jobs

# https://stackoverflow.com/questions/69100275/error-while-downloading-the-requirements-using-pip-install-setup-command-use-2
# Installing wheel makes the rest of the installation faster.
RUN pip3 install setuptools==58 wheel
RUN pip3 install -r /code/Rodan/requirements.txt

RUN chmod +x /run/install_python3_rodan_jobs
RUN /run/install_python3_rodan_jobs

  # Change the concurency for python3 jobs (Calvo)
RUN sed -i "s/=10/=1/g" /run/start-celery

# Script to wait for postgres and redis to be running before attempting to connect to them.
RUN chmod +x /run/wait-for-app

RUN sed -i 's/\r//' /opt/entrypoint
RUN chmod +x /opt/entrypoint

RUN sed -i 's/\r//' /run/start-celery
RUN chmod +x /run/start-celery

ENTRYPOINT ["/opt/entrypoint"]
