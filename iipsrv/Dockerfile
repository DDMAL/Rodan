FROM alpine:3

RUN apk update
RUN apk upgrade
RUN apk add --no-cache \
  autoconf \
  automake \
  build-base \
  jpeg-dev \
  libtool \
  m4 \
  make \
  pkgconfig \
  tiff-dev

RUN wget https://github.com/ruven/iipsrv/archive/refs/tags/iipsrv-1.1.zip
RUN unzip iipsrv-1.1.zip
WORKDIR iipsrv-iipsrv-1.1
RUN ./autogen.sh
RUN ./configure
RUN make

ENV JPEG_QUALITY 90
ENV FILESYSTEM_PREFIX /rodan/data
ENV VERBOSITY 2
ENV PORT 9003

EXPOSE ${PORT}


ENTRYPOINT ./src/iipsrv.fcgi --bind 0.0.0.0:${PORT}
