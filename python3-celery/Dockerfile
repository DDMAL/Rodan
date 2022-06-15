FROM debian:buster
ARG BRANCHES
ARG VERSION

RUN set -e \ 
  && apt-get -qq update \
  && apt-get install ffmpeg libsm6 libxext6 -y \
  && apt-get -qq install -y \
    git \
    python3 \
    python3-pip \
    apt-utils \
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
    # Remove when done
    vim 
   
  # Needed for pixel_wrapper (node_js)

RUN rm -rf /var/lib/apt/lists/*

COPY ./scripts/install_python3_rodan_jobs /run/
COPY ./scripts/install_rodan /run/
COPY ./scripts/start-celery /run/
COPY ./scripts/wait-for-app /run/

# Copying rodan core from build context into container
# Rodan folder MUST be uppercase, otherwise many unittests fail.
COPY ./rodan-main/code /code/Rodan

RUN set -x \
  && apt-get -qq install -y apt-transport-https curl gnupg >/dev/null \
  && curl -sL https://deb.nodesource.com/setup_10.x | bash - \
  && apt-get -qq install -y nodejs >/dev/null \
  #&& apt-get -qq install -y nodejs npm \ 
  && npm install -g npm@6.14.12 \
  && node -v \ 
  # Needed for Neon2-wrapper (yarn) - [TODO] - Test pixel with yarn also.
  && apt-get -qq remove cmdtest \
  && node -v \
  && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
  && node -v \
  && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
  && node -v \
  && apt-get -qq update && apt-get -qq install yarn -y >/dev/null \
  && mkdir -p /code/jobs \
  && node -v \
  # Install Python3 Rodan Jobs
  && chmod +x /run/install_python3_rodan_jobs \
  && chown www-data /run/install_python3_rodan_jobs \
  && node -v \
  && /run/install_python3_rodan_jobs 



