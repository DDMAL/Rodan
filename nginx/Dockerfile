FROM ddmal/rodan-client:fix_dev as webapp

# Add local configuration and build.
RUN rm -rf /code/configuration.json
COPY ./config/configuration.json /code/
RUN /code/node_modules/.bin/gulp dist


###########################################################
FROM ddmal/rodan-main:fix_dev as rodan-static

RUN touch /code/Rodan/database.log /code/Rodan/rodan.log

RUN export DJANGO_SECRET_KEY=localdev \
  && export DJANGO_ACCESS_LOG=None \
  && export DJANGO_DEBUG_LOG=None \
  && export DJANGO_ALLOWED_HOSTS=* \
  && export CELERY_JOB_QUEUE=None \
  # Check to see if the static folder exists
  && mkdir /code/Rodan/rodan/static \
  # If it does, erase everything.
  || rm -rf /code/Rodan/rodan/static/* \
  && python3 /code/Rodan/manage.py collectstatic --noinput


###########################################################
FROM nginx:1.19

# Install OS dependencies
RUN apt-get -qq update \
  && apt-get -qq install openssl certbot unzip -y \
  && rm -rf /var/lib/apt/lists/*

# Add configuration files.
COPY ./config/nginx.conf     /etc/nginx/nginx.conf
COPY ./config/ssl.conf       /etc/nginx/conf.d/ssl.conf
COPY ./config/ssl-http.conf  /etc/nginx/conf.d/ssl-http.conf
COPY ./config/error.conf     /etc/nginx/conf.d/error.conf
COPY ./config/rodan.conf     /etc/nginx/sites-available/rodan.conf
COPY ./config/rodan.stream   /etc/nginx/sites-available/rodan.stream

RUN mkdir -p /rodan/data
RUN chown -R www-data /rodan

# Add 40x and 50x pages.
RUN rm /usr/share/nginx/html/*
COPY ./html/ /var/www/default/

# Add Rodan Client
COPY --from=webapp /code/dist/* /var/www/default/dist/
RUN set -e \
  && mkdir /var/www/default/dist/resources \
  && mv /var/www/default/dist/favicon.ico /var/www/default/dist/resources/ \
  && mv /var/www/default/dist/grids-responsive-min.css /var/www/default/dist/resources/
# Add Rodan Static files
COPY --from=rodan-static /code/Rodan/staticfiles /rodan/static

# Create and add SSL certificates.
#RUN mkdir /etc/nginx/keys
#COPY ./certs/local_cert.pem     /etc/nginx/keys/cert.pem
#COPY ./certs/local_key.pem      /etc/nginx/keys/key.pem
#COPY ./certs/local_dhparam.pem  /etc/nginx/keys/dhparam.pem

RUN mkdir -p /etc/letsencrypt
RUN mkdir -p /var/www/letsencrypt/.well-known/acme-challenge

# This script corrects permissions in the file system
COPY ./scripts/setup /run/
RUN chmod +x /run/setup

# This script starts nginx for development
COPY ./scripts/start /run/
RUN chmod +x /run/start

# This script starts nginx for production
COPY ./scripts/start-production /run/
RUN chmod +x /run/start-production
