# Rodan client
- A GUI that allows you to interact with Rodan jobs and workflows. 

## Folder structure
> From https://github.com/DDMAL/Rodan/wiki/Repository-Structure

- `code`: submodule for the repository
- `config`: configuration files for the container
- `scripts`: point to start scripts and docker entry points for the container. These scripts exist to help you for that specific container. There can also be scripts to help build the service outside of the dockerfile.


---

**UPDATE:** You should not need to install rodan-client this way anymore. **Docker** does everything for us. 

## Prerequisites
Using your package manager, e.g., [`homebrew`](https://brew.sh) for MacOS; `apt` for Linux/WSL; `chocolatey` for Windows, install the following:
- Install `yarn` via Homebrew:
```sh
brew install yarn
```

- Install `gulp` if you have not already. You should install both `yarn` and `gulp` globally.
```sh
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


## Step-by-step to run Rodan Client on M1
1. Navigate to rodan. `cp rodan-client/local-dev/arm-compose.yml .`
2. Navigate to rodan. `make run_arm`
3. Navigate to rodan. `docker compose -f arm-compose.yml exec rodan-main /run/start`
4. Navigate to rodan. `docker compose -f arm-compose.yml exec celery /run/start-celery`
5. Navigate to rodan. `docker compose -f arm-compose.yml exec py3-celery /run/start-celery`
6. `docker compose -f arm-compose.yml exec rodan-client bash` to go to rodan-client container
7. Inside the container: `cd /code; yarn install`
8. Navigate to rodan-cleint: `cp local-dev/COPYconfiguration code/configuration.json`
9. Navigate to rodan-client: `cp local-dev/CPCONFIGFILE code/src/js/configuration.js`
10. Inside the container: `cd /code/node_modules/.bin` 
11. Inside the container: `yarn global add gulp`
12. Inside the container: `gulp`
13. Go to `localhost:8080` on your browser

To Run Rodan Client locally, you must have docker installed and have the docker images pulled from the nightly tag.
After installing docker, you can continue by replacing the docker-compose file with the one in the local-dev directory under the rodan-client directory. (dont forget to make the nginx container the same way as you do to run Rodan main for M1 systems)

After the installation, you have to `make run` and `docker compose exec rodan-main /run/start` to have the rodan-main container run.

Next, you will need to CLI into the rodan client and make some manual changes to the config.json file. do `docker compose exec rodan-client bash`.

Now, you are in the rodan-client container. Run `cd /code; yarn install`.

Move the COPYconfiguration file in the local-dev directory under rodan client to the rodan-client directory (These are all for the local development environment meaning that Rodan clone on your device and not the rodanclient container), to directory /code and name it `configuration.json`.

Replace /code/src/js/Configuration.js (this is in the container) content with the CPCONFIGFILE content under local-dev directory (local environment, not the container).

**NOTE**: If you cant replace the code using vim or your editor, you can copy the content, paste to the command line and use the command: `cat {paste the content} > {output_file}`

Continue by running the following commands in order
```
cd /code/node_modules/.bin
yarn global add gulp
gulp
```
Finally, go to localhost:8080, usr name and pwd are rodan.

