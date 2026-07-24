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
# Patch upstream OpenJPEG region-clamp bug in OpenJPEGImage::process().
# w0/h0 are END coordinates passed to
# opj_set_decode_area(codec, img, start_x, start_y, end_x, end_y),
# but the overrun clamp treats them as widths (x0 + w0) and reassigns
# w0 = image_widths[0] - x0. For any tile whose x0 > width/2 this makes
# end_x < start_x, so OpenJPEG gets a negative decode width and errors out
# -> the right/bottom half of every image 404s (and the boundary band
# garbles) when zooming. w0/h0 must be clamped to the image dimensions
# directly, not offset by x0/y0.
RUN sed -i 's/if( x0 + w0 > image_widths\[0\][[:space:]]*) w0 = image_widths\[0\][[:space:]]*- x0;/if( w0 > image_widths[0] ) w0 = image_widths[0];/' src/OpenJPEGImage.cc \
  && sed -i 's/if( y0 + h0 > image_heights\[0\][[:space:]]*) h0 = image_heights\[0\][[:space:]]*- y0;/if( h0 > image_heights[0] ) h0 = image_heights[0];/' src/OpenJPEGImage.cc \
  && grep -q 'if( w0 > image_widths\[0\] ) w0 = image_widths\[0\];' src/OpenJPEGImage.cc \
  && grep -q 'if( h0 > image_heights\[0\] ) h0 = image_heights\[0\];' src/OpenJPEGImage.cc
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