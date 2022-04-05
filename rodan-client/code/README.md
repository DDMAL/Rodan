# __rodan-client__

Rodan-Client is a GUI that allows you to interact with Rodan jobs and workflows. 

**UPDATE:** You should not need to install rodan-client this way anymore. `Rodan-Docker` does everything for us. 

## Prerequisites
Install `Homebrew`, `Yarn`, `Gulp` and `git` if you have not already. You should install both `yarn` and `gulp` globally.
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install yarn
yarn global add gulp
```

## Installation
- Clone project `git clone https://github.com/DDMAL/rodan-client`
- Change to the project directory and run `yarn install`
- Copy the `configuration.example.json` file, and rename it to `configuration.json`
- Edit the `SERVER_HOST` and `SERVER_PORT` accordingly
  - If you're using docker in local development, use `localhost` for the server, and port `8000`. You will also need to set `SERVER_HTTPS` to false unless you setup local SSL certificates.
- From the root project directory, travel to `./node_modules/.bin/`.
- Run `gulp`
