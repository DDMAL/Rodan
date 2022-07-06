# Rodan

- Rodan ![GitHub release](https://img.shields.io/github/release/ddmal/rodan) ![GitHub pull requests](https://img.shields.io/github/issues-pr/ddmal/rodan) ![GitHub issues](https://img.shields.io/github/issues/ddmal/rodan)
  - Master Branch ![GitHub last commit (branch)](https://img.shields.io/github/last-commit/ddmal/rodan/master)
  - Develop Branch ![GitHub last commit (branch)](https://img.shields.io/github/last-commit/ddmal/rodan/develop)

This repository contains Docker images that can be used to set up [Rodan](https://github.com/DDMAL/rodan) locally for development. These images can also be used in the future with slight modifications for deployment to a swarm production environment. Please see the wiki for more information about deploying Rodan. [Rodan-Docker Wiki](https://github.com/DDMAL/rodan-docker/wiki)

#### Objectives

- Simplify the installation process of Rodan on all platforms.
- Maintain clear installation documentation.

## Quick Start

If you are working on **Rodan** or **Rodan Jobs**

- Make sure you have Rodan submodule cloned in `${repository_root}/rodan/code` and **it is up to date** with the branch you wish to work with. The branches should be either `develop`, or the **name of the feature** you would like to include into develop. The `master` branch is only for version releases and is supposed to be a guaranteed working version.
- Follow the instructions here: https://github.com/DDMAL/rodan-docker/wiki/Working-on-Rodan
  - If working on jobs, you will need to install the jobs individually on your machine inside the docker environment. All dependencies for each job should already be installed. You can follow the same shell script used to install the jobs individually in the container here: `${repository_root}/scripts/install_rodan_jobs` and `${repository_root}/scripts/install_python3_rodan_jobs`.
  - Note the `BRANCHES` environment variable in the installation scripts, you can set the environment variable locally by running the following command: `export BRANCHES="develop"`.

If you are working on **Rodan-Client**

- Make sure you have Rodan-Client cloned in `${repository_root}/rodan-client/code` and it is up to date with the branch you wish to work with.
- Follow the instructions here: https://github.com/DDMAL/rodan-docker/wiki/Working-on-Rodan-Client

## Tips for Interacting with Running Containers

The following commands may seem familiar to you if you have worked with Posix systems, or bash shells in general. Many of the commands that exist for docker, by just adding the prefix `docker`.

- If you would like to see a list of all running containers on your machine, execute: `docker ps`
- To copy files between the container and the host, it is the same way you would use scp between different computers, execute: `docker cp`,
- Other commands like `docker top` are also available to monitor resources outside of the containers.

A similar concept to using `exec` is using SSH to connect to another computer. We use `exec` to connect to a specific container. It is much simpler to use `docker compose exec`, instead of the `docker exec`. Docker compose will search the configuration inside `docker-compose.yml` to know which service is being referenced. The format of the command works this way:

- `docker compose exec <service_name> <command>`
- The command could be anything eg: `/opt/some_directory/my_shell_script.sh`
- A command you will use frequently is: `docker compose exec rodan bash` or `docker compose exec celery bash` for investigating problems. **You should not be using this command to edit files, use `docker volumes` and your IDE outside of the container.**

Consult the documentation of the [Docker command line](https://docs.docker.com/engine/reference/commandline/cli/) for additional information.

## Automated Build

The images are rebuilt and pushed automatically on a nightly basis at 2am. This accomplished with a cron job. You must point the cron job to the nightly script on one of the staging virtual machines. Any account will do and no authentication required, add this line to the crontab. Docker hub will send a Slack notification if the image has built. We should expect 5 new images daily, or more if there was a new tagged release of any of them.

```shell
0 2 * * 1-5 /srv/webapps/rodan-docker/scripts/nightly
```

You may also force Docker Cloud to rebuild new images when new commits are pushed to a Git repository. Unfortunately, we had problems connecting the `rodan-docker` GitHub repository to Docker Cloud due to authentication issues, so we set up a private repository on Bitbucket instead.

## Additional Information

For more information about volumes in Docker, see [Use volumes](https://docs.docker.com/engine/admin/volumes/volumes/) in the Docker documentation. See also the docs for the [`volumes` section](https://docs.docker.com/compose/compose-file/#volumes) of the `docker compose.yml` file.
