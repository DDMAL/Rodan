FROM debian:buster
ARG BRANCHES
ARG VERSION

# Sometimes install_rodan_jobs will return `ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.`
# For this reason, we extend the timeout of pip.
ENV PIP_DEFAULT_TIMEOUT=100

# Update repository list.
# Install required packages for debian.
# [TODO] Recheck this list, organized it from memory. There could even be packages that are not necessary.
RUN set -e \
  # Project Dependencies
  && apt-get update \
  && apt-get -qq install -y \
    git \
    python \
    python-pip \
    python-dev \
    python-docutils \
    libpython-dev \
    cmake \
    g++ \
    apt-utils \
    # Gamera Dependencies
    autoconf \
    graphicsmagick \
    libtiff5-dev \
    libpng-dev \
    python-pygments \
    python-wxgtk3.0 \
    python-wxversion \
    lib32ncurses5-dev \
    # Libmei
    libboost-python-dev \
    libboost-thread-dev \
    libjpeg-dev \
    uuid-dev \
    libpq-dev \
    openjdk-11-jdk \
    # Silent the output
    >/dev/null \
  # Needed for pixel_wrapper (node_js)
  && apt-get -qq install -y apt-transport-https curl gnupg >/dev/null \
  && curl -sL https://deb.nodesource.com/setup_10.x | bash - \
  && apt-get -qq update \
  && apt-get -qq install -y nodejs >/dev/null \
  # Needed for Neon2-wrapper (yarn) - [TODO] - Test pixel with yarn also.
  && apt-get -qq remove cmdtest \
  && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
  && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
  && apt-get -qq update && apt-get -qq install yarn -y >/dev/null \
  # Needed for Ocropy (Text-Alignment)
  && apt -qq install -y \
    wget \
    python-scipy \
    python-matplotlib \
    python-lxml \
    >/dev/null \
  # [TODO] Check these
  && apt-get -qq install -y \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    lib32z1-dev \
    libxml2-utils \
    libvips42 \
    libvips-tools \
    libtool \
    subversion \
    pkg-config \
    >/dev/null 

# Clean out repository list.
RUN rm -rf /var/lib/apt/lists/*

# Install Gamera. This takes a very long time to build. Do not move it!
# RUN pip install git+https://github.com/hsnr-gamera/gamera.git --global-option="--nowx"
# pip broke again: https://github.com/pypa/pip/issues/6560
# Let's not rely on pip to install this again.

RUN set -e \
  && mkdir -p /rodan/data /code/jobs \
  && chown -R www-data /rodan \
  && git clone https://github.com/hsnr-gamera/gamera.git /code/gamera \
  # Without this gamera's setup can't find the version file.
  && cd /code/gamera \
  # && git reset --hard c77194d5e839204efc617971233967ba5a6c53bc \
  && git reset --hard  d8e4255a5e2d6d6e64528c8758d75f0afacf4d72 \
  && python setup.py install --nowx >/dev/null 2>&1
  # Prep for Rodan
  # && git clone -b ${BRANCHES} https://github.com/DDMAL/Rodan.git /code/Rodan

# Install framework dependencies for Rodan Jobs.
COPY ./rodan/scripts/install_rodan_job_dependencies /run/
COPY ./rodan/scripts/install_python2_rodan_jobs /run/
COPY ./rodan/scripts/install_rodan /run/
COPY ./rodan/scripts/wait-for-app /run/
COPY ./rodan/scripts/entrypoint /opt/
COPY ./rodan/scripts/start-celery /run/

# Copying rodan core from build context into container
# Rodan folder MUST be uppercase, otherwise many unittests fail.
COPY ./rodan/code /code/Rodan


RUN set -x \
  && chmod +x /run/install_rodan_job_dependencies \
  && chown www-data /run/install_rodan_job_dependencies \
  && /run/install_rodan_job_dependencies \
  # Install Rodan Jobs
  && chmod +x /run/install_python2_rodan_jobs \
  && chown www-data /run/install_python2_rodan_jobs \
  && /run/install_python2_rodan_jobs \
  # Install Rodan
  && chmod +x /run/install_rodan \
  && chown www-data /run/install_rodan \
  && pip install -U setuptools==44.0.0 \
  && sed -i "s/-e git+https:\/\/github.com\/deepio\/pybagit.git@4eea813148bc590896000f57cde35fb86443d2f4#egg=pybagit ; python_version >= '3.6'//" /code/Rodan/requirements.txt \
  && /run/install_rodan \
  # Script to wait for postgres and redis to be running before attempting to connect to them.
  && chmod +x /run/wait-for-app \
  && chown www-data /run/wait-for-app \
  # Runs on both Rodan service, and Rodan-Celery
  && sed -i 's/\r//' /opt/entrypoint \
  && chmod +x /opt/entrypoint \
  && chown www-data /opt/entrypoint \
  # This script starts Rodan-Celery
  && sed -i 's/\r//' /run/start-celery \
  && chmod +x /run/start-celery \
  && chown www-data /run/start-celery \
  && chown -R www-data /code/Rodan /code/jobs

ENTRYPOINT ["/opt/entrypoint"]
