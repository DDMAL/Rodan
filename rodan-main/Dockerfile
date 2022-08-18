FROM ddmal/rodan-python3-celery:nightly
ARG BRANCHES
ARG VERSION
ARG BUILD_HASH

# Install OpenJPEG dependencies.
RUN \
  # flip this to trigger a new layer because the scripts are cached.
  set -x \
  && mkdir /vendor || echo "Already exists" \
  && apt update \
  && apt -q install -y \
    libopenjp2-7 \
    libopenjp2-7-dev \
    libopenjp2-tools

# We need make to compile Grok.
RUN apt-get install -y make

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

# This script gets the gpu jobs into celery
COPY ./scripts/install_gpu_rodan_jobs /opt/install_gpu_rodan_jobs
COPY ./scripts/start /run/
RUN set -e \
  && chmod +x /opt/install_gpu_rodan_jobs \
  && chown www-data /opt/install_gpu_rodan_jobs \
  # This script starts Rodan
  && chmod +x /run/start \
  && chown www-data /run/start

RUN /opt/install_gpu_rodan_jobs

# Substitute the build hash for our actual build hash
RUN sed -i "s/__build_hash__ = \"local\"/__build_hash__ = \"${BUILD_HASH}\"/" /code/Rodan/rodan/__init__.py

ENTRYPOINT ["/opt/entrypoint"]
