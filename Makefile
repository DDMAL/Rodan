# Local-development shortcuts (docker-compose).
#
# Image build/push and cluster deploy now live in .github/workflows/build-and-deploy.yml
# (builds to GHCR, deploys to the k3s `rodan` namespace). The old Docker Swarm / DockerHub
# targets were removed when Rodan migrated to k3s.

# Portable replacement for `sed` or `gsed`
# See https://unix.stackexchange.com/questions/92895/how-can-i-achieve-portability-with-sed-i-in-place-editing
REPLACE := perl -i -pe

RODAN_PATH := ./rodan-main/code/rodan
JOBS_PATH := $(RODAN_PATH)/jobs

DOCKER_TAG := nightly

build:
	@echo "[-] Rebuilding Docker Images for Rodan..."
	# py3-celery first — rodan-main (the `rodan` service) and celery images are FROM it.
	@docker compose -f build.yml build --no-cache py3-celery
	# rodan(-main) and rodan-client next — nginx is FROM rodan-main.
	@docker compose -f build.yml build --no-cache --parallel rodan rodan-client
	@docker compose -f build.yml build --no-cache --parallel nginx gpu-celery postgres iipsrv
	@echo "[+] Done."

run: remote_jobs
	# Run local version for dev
	@DOCKER_TAG=$(DOCKER_TAG) docker compose up

run_client:
	# Run Rodan-Client for dev (needs local dev up and running)
	@docker run -p 8080:9002 -v `pwd`/rodan-client/code:/code ddmal/rodan-client:nightly bash

stop:
	@echo "[-] Stopping all running docker containers..."
	@docker stop `docker ps -aq | grep -v $$(docker ps -aq --filter "name=gpu_dont_kill_me")` >>/dev/null 2>&1 || echo "[+] No Containers Running"
	@echo "[+] Done."

clean:
	# Erase all docker data, this can be dangerous
	@echo "[-] Removing all docker containers..."
	@docker system prune -fa >>/dev/null 2>&1
	@echo "[+] Done."

clean_git:
	@echo "[-] Cleaning git..."
	@git reset --hard
	@git pull
	@echo "[+] Done."

health:
	@docker inspect --format "{{json .State.Health }}" $(log) | jq

# Neon's webpack build needs the exact toolchain baked into the rodan-python3-celery image
# (Alpine node 16 / yarn) and fails on newer host Node versions. So instead of building on the
# host, extract the already-built neon_wrapper (source + static/editor.html + Python package)
# out of that image — built by `make build`, or pulled from GHCR if absent.
$(JOBS_PATH)/neon_wrapper/static/editor.html:
	@echo "[-] Extracting pre-built neon_wrapper from rodan-python3-celery:$(DOCKER_TAG)..."
	@docker image inspect ghcr.io/ddmal/rodan-python3-celery:$(DOCKER_TAG) >/dev/null 2>&1 || \
		docker pull ghcr.io/ddmal/rodan-python3-celery:$(DOCKER_TAG)
	@# Remove any existing copy as root — the containers run as root and may own __pycache__
	@# files under the bind-mounted jobs dir that the host user cannot delete.
	@docker run --rm --entrypoint sh -v $(abspath $(JOBS_PATH)):/jobs ghcr.io/ddmal/rodan-python3-celery:$(DOCKER_TAG) -c "rm -rf /jobs/neon_wrapper"
	@cid=$$(docker create ghcr.io/ddmal/rodan-python3-celery:$(DOCKER_TAG)); \
		docker cp $$cid:/code/Rodan/rodan/jobs/neon_wrapper $(JOBS_PATH)/neon_wrapper; \
		docker rm $$cid >/dev/null
	@echo "[+] neon_wrapper ready."

$(JOBS_PATH)/pixel_wrapper/package.json:
	@cd $(JOBS_PATH); git clone --recurse-submodules -b develop https://github.com/DDMAL/pixel_wrapper.git

remote_jobs: $(JOBS_PATH)/pixel_wrapper/package.json $(JOBS_PATH)/neon_wrapper/static/editor.html
	@cd $(RODAN_PATH); $(REPLACE) "s/#py3 //g" ./settings.py
	@cd $(RODAN_PATH); $(REPLACE) "s/#gpu //g" ./settings.py

# Command Groups
clean_reset: stop clean build run
