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
# Patch upstream OpenJPEG 8-bit decode bug: the mask for 8-bit output data is
# 0x000000f (4-bit / low nibble only), which renders every 8-bit JP2 ~32x too
# dark. It must be 0x000000ff (full 8-bit byte). See src/OpenJPEGImage.cc.
RUN sed -i 's/& 0x000000f)/\& 0x000000ff)/' src/OpenJPEGImage.cc \
  && grep -q '& 0x000000ff)' src/OpenJPEGImage.cc
RUN ./autogen.sh
RUN ./configure --enable-openjpeg
RUN make

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