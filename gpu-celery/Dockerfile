# ARG UBUNTU_VERSION=24.04
# ARG CUDA=12.9.0
# ARG IMAGE_VER=cudnn-runtime-ubuntu$UBUNTU_VERSION

# ARG BASEIMAGE="nvidia/cuda:${CUDA}-${IMAGE_VER}"
ARG BASEIMAGE="tensorflow/tensorflow:latest-gpu"

FROM ${BASEIMAGE}

SHELL ["/bin/bash", "-c"]

RUN apt-get update
# RUN apt-get install -y --no-install-recommends \
#    wget \
#    ca-certificates \
#    git \
#    build-essential \
#    dh-make \
#    fakeroot \
#    devscripts \
#    lsb-release

# ENV LANG=C.UTF-8

# Install python
#RUN apt-get install -y --no-install-recommends \
#    python3 python3-pip python3-venv

# WORKDIR missing
# ENV VIRTUAL_ENV=.venv
# RUN python3 -m venv .venv
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# RUN source .venv/bin/activate
# RUN pip3 --no-cache-dir install --upgrade pip setuptools

# use .venv/bin/python3
# we want tensorflow 2.5.1?
# Other possible options: tensorflow, tensorflow-gpu, tf-nightly?, tf-nightly-gpu?
# RUN pip3 install tensorflow


# Install GPU Rodan Jobs

COPY ./scripts/install_gpu_rodan_jobs /opt/

# Install Rodan
# Runs on both Rodan service, and Rodan-Celery
COPY ./scripts/entrypoint /opt/
COPY ./scripts/start-celery /run/
COPY ./scripts/wait-for-app /run/

# Copying rodan core from build context into container
# Rodan folder MUST be uppercase, otherwise many unittests fail.
COPY ./rodan-main/code /code/Rodan

# necessary for scikit-image > 0.17, or else it will try to make a cache directory
# in a place where the www-data user does not have permissions to do so
ENV SKIMAGE_DATADIR="/tmp/.skimage_cache"

RUN set -x
RUN mkdir -p /code/jobs
  # Install GPU Jobs
RUN chmod +x /opt/install_gpu_rodan_jobs
RUN /opt/install_gpu_rodan_jobs ## issue here!!!
RUN sed -i "s/lxml/#lxml/g" /code/Rodan/requirements.txt
  # && sed -i "s/pybagit==1.5.0/-e git:\/\/github.com\/deepio\/pybagit.git@a27c9e0fc3bdf99dab8bd327f3ce9ea884abd6b4#egg=pybagit/g" /code/Rodan/requirements.txt \
  # Add Entrypoints
RUN sed -i 's/\r//' /opt/entrypoint \
RUN chmod +x /opt/entrypoint \
  # Add Celery script
  && chmod +x /run/start-celery \
  # Change the concurency for gpu jobs because Calvo is very expensive
  && sed -i "s/=10/=1/g" /run/start-celery \
  # Script to wait for postgres and redis to be running before attempting to connect to them.
  && chmod +x /run/wait-for-app

# Install Rodan.
RUN pip3 install -r /code/Rodan/requirements.txt

RUN pip3 uninstall -y opencv-python opencv-python-headless
RUN pip3 install opencv-python-headless==4.1.2.30

ENTRYPOINT ["/opt/entrypoint"]

