FROM ddmal/rodan-python2-celery:nightly
ARG BRANCHES
ARG VERSION

# Install Grok
RUN wget https://github.com/GrokImageCompression/grok/releases/download/v9.7.6/grok-ubuntu-latest.zip
RUN unzip /grok-ubuntu-latest.zip
RUN mkdir -p /vendor/build/bin
RUN cp /grok-ubuntu-latest/bin/* /vendor/build/bin

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
