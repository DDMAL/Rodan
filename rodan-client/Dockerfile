FROM debian
EXPOSE 9002

# Install OS packages.
RUN apt-get -qq update \
  && apt-get -qq install -y \
    git \
    gnupg2 \
    libgif-dev \
    curl \
    build-essential \
  # Add npm
  # && curl -sL https://deb.nodesource.com/setup_12.x | bash - \
  # && apt-get install -yq \
  #   nodejs
  # Add yarn
  && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
  && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
  && apt -qq update \
  && apt -qq install -y \
    yarn \
  && rm -rf /var/lib/apt/lists/*

# Install node project.
COPY code/ /code/
RUN set -x \
  && cd /code \
  # && npm install
  && yarn install

# On some machines, the webpack dev server on the container won't accept connections from the host on localhost.
# Make the development server listen on 0.0.0.0 instead to accept connections from all addresses.
ENV RODAN_CLIENT_DEVELOP_HOST 0.0.0.0
WORKDIR /code/node_modules/.bin

COPY ./config/configuration.json /code/configuration.json

# Template start script, in case the startup gets longer.
COPY ./scripts/start /run/
RUN sed -i 's/\r//' /run/start
RUN chmod +x /run/start
