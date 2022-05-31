FROM alpine:3

RUN apk update
RUN apk upgrade
RUN apk add --no-cache \
  autoconf \
  automake \
  build-base \
  libtool \
  libpng-dev \
  m4 \
  make \
  openjpeg-dev \
  pkgconfig \
  tiff-dev

RUN wget https://github.com/ruven/iipsrv/archive/refs/heads/master.zip
RUN unzip master.zip
WORKDIR iipsrv-master
RUN ./autogen.sh
RUN ./configure --enable-openjpeg
RUN make

ENV JPEG_QUALITY 90
ENV FILESYSTEM_PREFIX /rodan/data/
ENV VERBOSITY 2
ENV PORT 9003

EXPOSE ${PORT}


ENTRYPOINT ./src/iipsrv.fcgi --bind 0.0.0.0:${PORT}
