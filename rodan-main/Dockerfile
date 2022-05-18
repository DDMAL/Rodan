FROM ddmal/rodan-python2-celery:nightly
ARG BRANCHES
ARG VERSION

# Install OpenJPEG
RUN \
  # flip this to trigger a new layer because the scripts are cached.
  set -x \
  && mkdir /vendor || echo "Already exists" \
  && apt update \
  && apt -q install -y \
    libopenjp2-7 \
    libopenjp2-7-dev \
    libopenjp2-tools

# Install Grok
RUN \
  cd /vendor \
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

# Install IIPSRV to serve image files and manifests for the Diva.js viewer used to preview TIFF and JPEG2000 resources.
RUN \
  cd /vendor \
  && git clone https://github.com/ruven/iipsrv \
  && cd iipsrv \
  && git checkout 6d8390f48fe242369b65ef63539bc15b5b9e0f22 \
  && ./autogen.sh \
  && ./configure 'CFLAGS=-g -O2 -Wall -Wextra -Wno-unused-parameter' 'CXXFLAGS=-g -O2 -Wall -Wextra -Wno-unused-parameter' 'LDFLAGS=-g' '--enable-openjpeg' \
  && make

# Install pixel and Neon
RUN git clone --recurse-submodules -b develop https://github.com/DDMAL/pixel_wrapper.git /code/Rodan/rodan/jobs/pixel_wrapper
RUN git clone --recurse-submodules -b develop https://github.com/DDMAL/neon_wrapper.git /code/Rodan/rodan/jobs/neon_wrapper
RUN cd /code/Rodan/rodan/jobs/neon_wrapper && \
  git submodule update --init && \
  git submodule update --remote
RUN cd /code/Rodan/rodan/jobs/neon_wrapper && \
  yarn install && yarn build
RUN sed -i "s/#py2 //g" /code/Rodan/rodan/settings.py
RUN sed -i "s/#py3 //g" /code/Rodan/rodan/settings.py
RUN sed -i "s/#gpu //g" /code/Rodan/rodan/settings.py

# This script gets the python3 jobs into celery
COPY ./scripts/install_python3_rodan_jobs /opt/install_python3_rodan_jobs
COPY ./scripts/install_gpu_rodan_jobs /opt/install_gpu_rodan_jobs
COPY ./scripts/start /run/
RUN set -e \
  && chmod +x \
    /opt/install_python3_rodan_jobs \
    /opt/install_gpu_rodan_jobs \
  && chown www-data \
    /opt/install_python3_rodan_jobs \
    /opt/install_gpu_rodan_jobs \
  # This script starts Rodan
  && chmod +x /run/start \
  && chown www-data /run/start

RUN \
  /opt/install_python3_rodan_jobs \
  && /opt/install_gpu_rodan_jobs \
  && /run/install_rodan

ENTRYPOINT ["/opt/entrypoint"]
