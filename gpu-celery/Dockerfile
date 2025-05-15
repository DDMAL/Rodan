# Based on the tensorflow version used in the old Dockerfile
# - Dockerfile from PR#751: https://github.com/DDMAL/Rodan/blob/d28e06a0a6c2440fa76b47f46cf13d269de1952f/gpu-celery/Dockerfile
# - Old verison of the Dockerfile


# ---- Builder image ----
FROM alpine:3 AS builder
ARG BRANCH
ENV BRANCH="${BRANCH:-develop}"
RUN apk update
RUN apk add git
# Download Rodan from the repository, develop branch
WORKDIR /
RUN git clone --recurse-submodules -b "${BRANCH}" https://github.com/DDMAL/Rodan


# ---- Tensorflow image ----
# FROM nvidia/cuda:12.9.0-runtime-ubuntu24.04
FROM tensorflow/tensorflow:2.19.0-gpu
SHELL ["/bin/bash", "-c"]

# Working from the root folder
WORKDIR /

# Update packages
RUN apt-get update 

# Install 
# RUN apt-get install python3 python3-pip python3-venv git -y

RUN apt-get install -yqq git \
    python3-lxml \
    # Psycopg2 dependencies
    libpq-dev \
    # OpenCV dependencies
    libsm6 libxext6 libxrender-dev libglib2.0-data \
    python3-opencv \
    # For resource identification
    libmagic-dev \
    unzip

RUN rm -rf /var/lib/apt/lists/*

# Bandaid fix for the cannot import name '_registerMatType' from 'cv2.cv2' issue
# RUN pip uninstall opencv-python-headless && pip install opencv-python-headless==4.1.2.30

# Python virtual environment
ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# --- Install GPU Rodan Jobs ---
# Copy files from scripts to /opt/ and /run/
COPY ./scripts/install_gpu_rodan_jobs /opt/
COPY ./scripts/entrypoint /opt/
COPY ./scripts/start-celery /run/
COPY ./scripts/wait-for-app /run/
COPY ./rodan-main/code /code/Rodan

# Runs on both Rodan service, and Rodan-Celery
# Copying rodan core from build context into container
# Rodan folder MUST be uppercase, otherwise many unittests fail.

# necessary for scikit-image > 0.17, or else it will try to make a cache directory
# in a place where the www-data user does not have permissions to do so
ENV SKIMAGE_DATADIR="/tmp/.skimage_cache"


# RUN apt-get update
# RUN apt-get install git -y
# RUN apt-get upgrade -y
# RUN pip install --upgrade pip

RUN set -x
RUN mkdir -p /code/jobs
  # Install GPU Jobs
RUN chmod +x /opt/install_gpu_rodan_jobs
RUN /opt/install_gpu_rodan_jobs ## issue here!!!
# RUN sed -i "s/lxml/#lxml/g" /code/Rodan/requirements.txt
  # && sed -i "s/pybagit==1.5.0/-e git:\/\/github.com\/deepio\/pybagit.git@a27c9e0fc3bdf99dab8bd327f3ce9ea884abd6b4#egg=pybagit/g" /code/Rodan/requirements.txt \
  # Add Entrypoints
#RUN sed -i 's/\r//' /opt/entrypoint \
#RUN chmod +x /opt/entrypoint \
  # Add Celery script
#RUN chmod +x /run/start-celery \
  # Change the concurency for gpu jobs because Calvo is very expensive
#RUN sed -i "s/=10/=1/g" /run/start-celery \
  # Script to wait for postgres and redis to be running before attempting to connect to them.
#RUN chmod +x /run/wait-for-app

# Install Rodan.
# RUN pip install -r /code/Rodan/requirements.txt

# RUN pip uninstall -y opencv-python opencv-python-headless
# RUN pip install opencv-python-headless==4.1.2.30

# ENTRYPOINT ["/opt/entrypoint"]

