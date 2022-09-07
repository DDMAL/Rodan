FROM alpine:3 AS builder
ARG BRANCH
ENV BRANCH="${BRANCH:-develop}"
RUN apk update
RUN apk add git
# Download Rodan
WORKDIR /
RUN git clone --recurse-submodules -b "${BRANCH}" https://github.com/ddmal/Rodan

FROM tensorflow/tensorflow:2.10.0rc1-gpu
RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -yqq \
    git \
    python3-lxml \
    # Psycopg2 dependencies
    libpq-dev \
    # OpenCV dependencies
    libsm6 libxext6 libxrender-dev libglib2.0-data \
    python3-opencv \
    # For resource identification
    libmagic-dev \
    unzip \
    # Remove when done
    vim

# Install GPU Rodan Jobs
COPY ./scripts/install_gpu_rodan_jobs /opt/
# Runs on both Rodan service, and Rodan-Celery
COPY ./scripts/start-celery /run/
COPY ./scripts/wait-for-app /run/

# Copying rodan core from build context into container
# Rodan folder MUST be uppercase, otherwise many unittests fail.
#TODO(buser): Swap this line out once pushed to develop.
COPY ./rodan-main/code /code/Rodan
# COPY --from=builder /Rodan/rodan-main/code /code/Rodan

RUN mkdir -p /code/jobs

# Install GPU Jobs
RUN chmod +x /opt/install_gpu_rodan_jobs
RUN chown www-data /opt/install_gpu_rodan_jobs
RUN /opt/install_gpu_rodan_jobs

# Install Rodan
RUN sed -i "s/pip /pip3 /g" /run/install_rodan
RUN sed -i "s/lxml/#lxml/g" /code/Rodan/requirements.txt
RUN sed -i "s/pybagit==1.5.0/-e git:\/\/github.com\/deepio\/pybagit.git@a27c9e0fc3bdf99dab8bd327f3ce9ea884abd6b4#egg=pybagit/g" /code/Rodan/requirements.txt


# Install Rodan
RUN chmod +x /run/install_rodan
RUN chown www-data /run/install_rodan
RUN /run/install_rodan

# Add Celery script
RUN chmod +x /run/start-celery
RUN chown www-data /run/start-celery

# Change the concurency for gpu jobs because Calvo is very expensive
RUN sed -i "s/=10/=1/g" /run/start-celery

# Script to wait for postgres and redis to be running before attempting to connect to them.
RUN chmod +x /run/wait-for-app
RUN chown www-data /run/wait-for-app
RUN chown -R www-data /code/Rodan /code/jobs

ENTRYPOINT ["/run/start-celery"]
