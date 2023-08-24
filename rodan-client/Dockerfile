# Alpine 3.15 is the last version to support Python 2.
FROM node:12.22.6-alpine as builder

# Install OS packages.
RUN apk add --no-cache \
  giflib-dev

RUN apk add bash

WORKDIR code

# Install Yarn packages.
COPY code/package.json code/yarn.lock ./
RUN yarn install --inline-builds && yarn cache clean

# Install node project.
COPY code/ .

# On some machines, the webpack dev server on the container won't accept connections from the host on localhost.
# Make the development server listen on 0.0.0.0 instead to accept connections from all addresses.
ENV RODAN_CLIENT_DEVELOP_HOST 0.0.0.0

# Build the project.
COPY ./config/configuration.json configuration.json
RUN yarn run dist

# Host the project.
FROM nginx:alpine
EXPOSE 80

# Copy nginx conf.
COPY scripts/nginx.conf /etc/nginx/nginx.conf

WORKDIR /client

# Copy project from builder.
COPY --from=builder /code/dist/ .
#RUN mkdir resources \
#  && mv favicon.iso resources \
#  && mv grids-responsive-min.css resources

# Host server.
CMD nginx
