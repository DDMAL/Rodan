FROM ddmal/rodan-main:${VERSION} as rodan-static

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
COPY ./config/error.conf     /etc/nginx/conf.d/error.conf
COPY ./config/rodan.conf     /etc/nginx/sites-available/rodan.conf

RUN mkdir -p /rodan/data
RUN chown -R www-data /rodan

# Add 40x and 50x pages.
RUN rm /usr/share/nginx/html/*
COPY ./html/ /var/www/default/

# Add Rodan Static files
COPY --from=rodan-static /code/Rodan/staticfiles /rodan/static

COPY ./scripts/setup /run/
RUN chmod +x /run/setup

# This script starts nginx
COPY ./scripts/start /run/
RUN chmod +x /run/start
