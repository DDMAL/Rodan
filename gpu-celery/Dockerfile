# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
#
# THIS IS A GENERATED DOCKERFILE.
#
# This file was assembled from multiple pieces, whose use is documented
# throughout. Please refer to the TensorFlow dockerfiles documentation
# for more information.

ARG UBUNTU_VERSION=18.04
ARG CUDA=11.2
FROM nvidia/cuda${ARCH:+-$ARCH}:${CUDA}.1-base-ubuntu${UBUNTU_VERSION} as base
# ARCH and CUDA are specified again because the FROM directive resets ARGs
# (but their default value is retained if set previously)
ARG ARCH
ARG CUDA
ARG CUDNN=8.1.0.77-1
ARG CUDNN_MAJOR_VERSION=8
ARG LIB_DIR_PREFIX=x86_64
ARG LIBNVINFER=7.2.2-1
ARG LIBNVINFER_MAJOR_VERSION=7

# The following two arguments are rodan-specific
ARG BRANCHES
ARG VERSION

# Needed for string substitution
SHELL ["/bin/bash", "-c"]
# Pick up some TF dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cuda-command-line-tools-${CUDA/./-} \
        libcublas-${CUDA/./-} \
        cuda-nvrtc-${CUDA/./-} \
        libcufft-${CUDA/./-} \
        libcurand-${CUDA/./-} \
        libcusolver-${CUDA/./-} \
        libcusparse-${CUDA/./-} \
        curl \
        libcudnn8=${CUDNN}+cuda${CUDA} \
        libfreetype6-dev \
        libhdf5-serial-dev \
        libzmq3-dev \
        pkg-config \
        software-properties-common \
        unzip \
		wget
# added wget		

# Install TensorRT if not building for PowerPC
# NOTE: libnvinfer uses cuda11.1 versions
# RUN [[ "${ARCH}" = "ppc64le" ]] || { apt-get update && \
#         apt-get install -y --no-install-recommends libnvinfer${LIBNVINFER_MAJOR_VERSION}=${LIBNVINFER}+cuda11.1 \
#         libnvinfer-plugin${LIBNVINFER_MAJOR_VERSION}=${LIBNVINFER}+cuda11.1 \
#         && apt-get clean \
#         && rm -rf /var/lib/apt/lists/*; }

# For CUDA profiling, TensorFlow requires CUPTI.
ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:/usr/local/cuda/lib64:/usr/local/cuda-11.1/lib64:$LD_LIBRARY_PATH

# Link the libcuda stub to the location where tensorflow is searching for it and reconfigure
# dynamic linker run-time bindings
RUN ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 \
    && echo "/usr/local/cuda/lib64/stubs" > /etc/ld.so.conf.d/z-cuda-stubs.conf \
    && ldconfig

# See http://bugs.python.org/issue19846
ENV LANG C.UTF-8

# This section differs from the default tensorflow2.5.1 Dockerfile, because we specifically add python 3.7;
ARG PYTHON=python3.7
ARG TF_PACKAGE=tensorflow
ARG TF_PACKAGE_VERSION=2.5.1


RUN apt-get install --reinstall ca-certificates

RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y ${PYTHON} \
  && wget https://bootstrap.pypa.io/get-pip.py \
  && ${PYTHON} get-pip.py \
  && ln -sf /usr/bin/${PYTHON} /usr/local/bin/python3 \
  && ln -sf /usr/local/bin/pip /usr/local/bin/pip3 \
  && pip3 --no-cache-dir install --upgrade pip setuptools==57.0.0 \
  # Some TF tools expect a "python" binary
  && ln -s $(which python3) /usr/local/bin/python \
  && python3 -m pip install --no-cache-dir ${TF_PACKAGE}${TF_PACKAGE_VERSION:+==${TF_PACKAGE_VERSION}}

# RUN ln -s $(which python3) /usr/local/bin/python

# Options:
#   tensorflow
#   tensorflow-gpu
#   tf-nightly
#   tf-nightly-gpu
# Set --build-arg TF_PACKAGE_VERSION=1.11.0rc0 to install a specific version.
# Installs the latest version by default.

# COPY bashrc /etc/bash.bashrc
# RUN chmod a+rwx /etc/bash.bashrc

# This ends the material obtained from TensorFlow's dockerfile. the remainder is rodan-docker-specific setup.

# FROM base
RUN set -e \
  && apt-get update \
  && DEBIAN_FRONTEND="noninteractive" apt-get install -yqq \
    git \
    # Python lxml dependencies
    python3.7-dev \
    python3-opencv \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    lib32ncurses5-dev \
    # Psycopg2 dependencies
    libpq-dev \
    # For resource identification
    libmagic-dev \
    unzip \
    # Remove when done
    vim

RUN rm -rf /var/lib/apt/lists/*

# Install GPU Rodan Jobs
COPY ./scripts/install_gpu_rodan_jobs /opt/
# Install Rodan
COPY ./scripts/install_rodan /run/
# Runs on both Rodan service, and Rodan-Celery
COPY ./scripts/entrypoint /opt/
COPY ./scripts/start-celery /run/
COPY ./scripts/wait-for-app /run/

# Copying rodan core from build context into container
# Rodan folder MUST be uppercase, otherwise many unittests fail.
COPY ./rodan-main/code /code/Rodan

# necessary for scikit-image > 0.17, or else it will try to make a cache directory
# in a place where the www-data user does not have permissions to do so
ENV SKIMAGE_DATADIR "/tmp/.skimage_cache"


RUN set -x \
  # Create Folders
  && mkdir -p /code/jobs \
  # Install GPU Jobs
  && chmod +x /opt/install_gpu_rodan_jobs \
  && chown www-data /opt/install_gpu_rodan_jobs \
  && /opt/install_gpu_rodan_jobs \
  # Install Rodan
  && sed -i "s/pip /pip3 /g" /run/install_rodan \
  && sed -i "s/lxml/#lxml/g" /code/Rodan/requirements.txt \
  # && sed -i "s/pybagit==1.5.0/-e git:\/\/github.com\/deepio\/pybagit.git@a27c9e0fc3bdf99dab8bd327f3ce9ea884abd6b4#egg=pybagit/g" /code/Rodan/requirements.txt \
  # Add Entrypoints
  && sed -i 's/\r//' /opt/entrypoint \
  && chmod +x /opt/entrypoint \
  && chown www-data /opt/entrypoint \
  # Install Rodan
  && chmod +x /run/install_rodan \
  && chown www-data /run/install_rodan \
  && /run/install_rodan \
  # Add Celery script
  && chmod +x /run/start-celery \
  && chown www-data /run/start-celery \
  # Change the concurency for gpu jobs because Calvo is very expensive
  && sed -i "s/=10/=1/g" /run/start-celery \
  # Script to wait for postgres and redis to be running before attempting to connect to them.
  && chmod +x /run/wait-for-app \
  && chown www-data /run/wait-for-app \
  && chown -R www-data /code/Rodan /code/jobs

ENTRYPOINT ["/opt/entrypoint"]
