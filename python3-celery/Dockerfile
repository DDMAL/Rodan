FROM debian:buster
ARG BRANCHES
ARG VERSION

RUN set -e \ 
  && apt update \
  #&& apt upgrade \
  && apt-get install ffmpeg libsm6 libxext6 -y \
  && apt-get -qq install -y \
    git \
    python3 \
    python3-pip \
    apt-utils \
    curl \
    #gamera-4 dependencies 
    libpng-dev \
    libtiff5-dev \
    # Opencv Dependency  
    python3-opencv \
    # Python lxml dependencies
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    lib32ncurses5-dev \
    # Psycopg2 dependencies
    libpq-dev \
    # >/dev/null
    #needed for text alignment
    wget \
    python-scipy \
    python-matplotlib \
    python-lxml \
    >/dev/null \
    # Remove when done
    vim 


RUN rm -rf /var/lib/apt/lists/*

COPY ./scripts/install_python3_rodan_jobs /run/
COPY ./scripts/install_rodan /run/
COPY ./scripts/start-celery /run/
COPY ./scripts/entrypoint /opt/
COPY ./scripts/wait-for-app /run/

# Copying rodan core from build context into container
# Rodan folder MUST be uppercase, otherwise many unittests fail.
COPY ./rodan-main/code /code/Rodan

RUN set -x \
  # Install Python3 Rodan Jobs
  && chmod +x /run/install_python3_rodan_jobs \
  && chown www-data /run/install_python3_rodan_jobs \
  && /run/install_python3_rodan_jobs \ 
    # Install Rodan
  # Django-Guardian suddenly failed to build.
  # https://github.com/DDMAL/rodan-docker/issues/60
  && pip3 install -U pip \
  && pip3 install setuptools==57.0.0 \
  && sed -i "s/pip /pip3 /g" /run/install_rodan \
  && sed -i "s/lxml/#lxml/g" /code/Rodan/requirements.txt \
  && sed -i "s/pybagit==1.5.0/-e git:\/\/github.com\/deepio\/pybagit.git@a27c9e0fc3bdf99dab8bd327f3ce9ea884abd6b4#egg=pybagit/g" /code/Rodan/requirements.txt \
  && chmod +x /run/install_rodan \
  && chown www-data /run/install_rodan \
  && /run/install_rodan \
  # Change the concurency for python3 jobs (Calvo)
  && sed -i "s/=10/=1/g" /run/start-celery \
  # Script to wait for postgres and redis to be running before attempting to connect to them.
  && chmod +x /run/wait-for-app \
  && chown www-data /run/wait-for-app \
  && chown -R www-data /code/Rodan /code/jobs \
  && pip3 install opencv-python==4.5.5.64 \
  #why is cv installed here?
  # # Runs on both Rodan service, and Rodan-Celery
  && sed -i 's/\r//' /opt/entrypoint \
  && chmod +x /opt/entrypoint \
  && chown www-data /opt/entrypoint \
  # This script starts Rodan-Celery
  && sed -i 's/\r//' /run/start-celery \
  && chmod +x /run/start-celery \
  && chown www-data /run/start-celery \
  && chown -R www-data /code/Rodan /code/jobs

ENTRYPOINT ["/opt/entrypoint"]

