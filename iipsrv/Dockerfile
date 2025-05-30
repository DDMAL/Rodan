# ---- Install and Build `iipsrv` ----
FROM alpine:3.18.5 AS builder

RUN apk add --no-cache \
  autoconf \
  automake \
  build-base \
  libtool \
  libpng-dev \
  openjpeg-dev \
  tiff-dev

RUN wget https://github.com/ruven/iipsrv/archive/refs/heads/master.zip && unzip master.zip
WORKDIR /iipsrv-master
RUN ./autogen.sh
RUN ./configure --enable-openjpeg
RUN make

# ---- Run the `iipsrv` server ----
FROM alpine:3.18.5

RUN apk add --no-cache \
  libgcc \
  libstdc++ \
  libgomp \
  libpng \
  openjpeg \
  tiff

COPY --from=builder /iipsrv-master/src/iipsrv.fcgi /fcgi-bin/iipsrv.fcgi

ENV JPEG_QUALITY 90
ENV FILESYSTEM_PREFIX /rodan/data/
ENV VERBOSITY 2
ENV PORT 9003

EXPOSE ${PORT}

ENTRYPOINT /fcgi-bin/iipsrv.fcgi --bind 0.0.0.0:${PORT}