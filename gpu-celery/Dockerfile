# GPU celery worker — TensorFlow 2.15 on CUDA 12 for Hopper (sm_90).
#
# The CUDA 12 runtime libraries are pulled as pip wheels via `tensorflow[and-cuda]`, so the
# image bakes in NO CUDA toolkit and only needs the host NVIDIA driver (supplied by the k8s
# `nvidia` RuntimeClass — see k8s/33-gpu-celery.yaml). This replaces the old hand-assembled
# nvidia/cuda:11.2 + TF 2.5.1 + py3.7 base, which cannot run on Hopper.
#
# This worker serves only the BASE + GPU job queues (CELERY_JOB_QUEUE=GPU), so it needs no
# Gamera. GPU jobs: Paco_classifier, background_removal, SAE_binarization (TF 2.15),
# staff_distance (skimage/cv2), and text_alignment (Calamari-OCR / ocrd-fork-tfaip 1.2.7).
FROM python:3.11-slim

ARG BRANCHES
ARG VERSION

# Scripts (entrypoint waits for postgres/redis then execs the arg = /run/start-celery).
COPY ./scripts/install_gpu_rodan_jobs /opt/
COPY ./scripts/entrypoint /opt/
COPY ./scripts/start-celery /run/
COPY ./scripts/wait-for-app /run/

# Rodan core. The folder MUST be uppercase or many unittests fail.
COPY ./rodan-main/code /code/Rodan

# scikit-image otherwise caches under $HOME, which www-data cannot create.
ENV SKIMAGE_DATADIR="/tmp/.skimage_cache"

# The old nvidia/cuda base set this; python:3.11-slim does not. The NVIDIA container
# runtime reads it to decide which driver features to inject — "compute" is required for
# CUDA (without it you get nvidia-smi but cuInit -> CUDA_ERROR_NO_DEVICE). NVIDIA_VISIBLE_DEVICES
# is intentionally left to the k8s device plugin. (Note: the GPU also needs a valid vGPU
# license on the host, or CUDA is blocked regardless.)
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# System deps: git (clones the GPU job repos), build-essential (native pip builds),
# libmagic1 (python-magic), libpq-dev (psycopg2), and the runtime libs opencv-python needs.
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    curl \
    git \
    libmagic1 \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    wget \
  && rm -rf /var/lib/apt/lists/*

# setuptools<80 keeps the legacy `setup.py install` used by the GPU job packages working.
RUN pip3 install --no-cache-dir "setuptools<80" wheel

# TensorFlow 2.15 with the bundled CUDA 12 wheels (Hopper sm_90 support).
RUN pip3 install --no-cache-dir "tensorflow[and-cuda]==2.15.1"

# Rodan Python deps.
RUN pip3 install --no-cache-dir -r /code/Rodan/requirements.txt

# GPU job packages (py311 branches + text_alignment's calamari). Their `tensorflow==2.15.1`
# pin is already satisfied by tensorflow[and-cuda] above, so pip does not reinstall TF.
RUN set -e \
  && mkdir -p /code/jobs \
  && chmod +x /opt/install_gpu_rodan_jobs \
  && /opt/install_gpu_rodan_jobs

# GPU jobs are expensive — one task per worker at a time.
RUN sed -i "s/--concurrency=10/--concurrency=1/g" /run/start-celery \
  && sed -i 's/\r//' /opt/entrypoint \
  && chmod +x /opt/entrypoint /run/start-celery /run/wait-for-app

ENTRYPOINT ["/opt/entrypoint"]
