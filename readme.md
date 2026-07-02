# Rodan

- Rodan ![GitHub release](https://img.shields.io/github/release/ddmal/rodan) ![GitHub pull requests](https://img.shields.io/github/issues-pr/ddmal/rodan) ![GitHub issues](https://img.shields.io/github/issues/ddmal/rodan)
  - Master Branch ![GitHub last commit (branch)](https://img.shields.io/github/last-commit/ddmal/rodan/master)
  - Develop Branch ![GitHub last commit (branch)](https://img.shields.io/github/last-commit/ddmal/rodan/develop)

This repository contains Docker images that can be used to set up [Rodan](https://github.com/DDMAL/rodan) locally for development. The same images are deployed to **Kubernetes (k3s)** in production — see [`k8s/`](./k8s) (and [`k8s/README.md`](./k8s/README.md)) for the manifests and deployment runbook. For more general information, see the [Rodan Wiki](https://github.com/DDMAL/Rodan/wiki).

#### Objectives

- Simplify the installation process of Rodan on all platforms.
- Maintain clear installation documentation.

## Quick Start

If you are working on **Rodan** or **Rodan Jobs**

- Make sure you have Rodan submodule cloned in `${repository_root}/rodan/code` and **it is up to date** with the branch you wish to work with. The branches should be either `develop`, or the **name of the feature** you would like to include into develop. The `master` branch is only for version releases and is supposed to be a guaranteed working version.
- Follow the instructions here: https://github.com/DDMAL/Rodan/wiki/Working-on-Rodan
  - Note the `BRANCHES` environment variable in the installation scripts, you can set the environment variable locally by running the following command: `export BRANCHES="develop"`.

If you are working on **Rodan-Client**

- Make sure you have Rodan-Client cloned in `${repository_root}/rodan-client/code` and it is up to date with the branch you wish to work with.
- Follow the instructions here: https://github.com/DDMAL/Rodan/wiki/Working-on-Rodan-Client

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

## CI/CD

Image builds, pushes, and deploys are handled by GitHub Actions in [`.github/workflows/build-and-deploy.yml`](./.github/workflows/build-and-deploy.yml):

- **Build & push** — all seven images are built and pushed to the private GitHub Container Registry at `ghcr.io/ddmal/<name>`. Triggers: push to `develop` → `:nightly`; a `v*` git tag → `:<version>`; pull requests build only (no push). Every pushed build also gets an immutable `:sha-<gitsha>` tag.
- **Deploy** — on a `v*` tag or manual `workflow_dispatch`, the app-tier Deployments in the k3s `rodan` namespace are rolled to the new `:sha-<gitsha>` images (via `kubectl set image`). `postgres`/`redis`/`rabbitmq` are left untouched.

See [`k8s/README.md`](./k8s/README.md) for the full deployment/runbook details.

## Additional Information

For more information about volumes in Docker, see [Use volumes](https://docs.docker.com/engine/admin/volumes/volumes/) in the Docker documentation. See also the docs for the [`volumes` section](https://docs.docker.com/compose/compose-file/#volumes) of the `docker-compose.yml` file.
