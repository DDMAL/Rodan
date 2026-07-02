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
	@docker compose -f build.yml build --no-cache --parallel nginx gpu-celery postgres
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

$(JOBS_PATH)/neon_wrapper/Neon/package.json:
	@cd $(JOBS_PATH); \
		git clone --recurse-submodules -b develop https://github.com/DDMAL/neon_wrapper.git

$(JOBS_PATH)/neon_wrapper/static/editor.html: $(JOBS_PATH)/neon_wrapper/Neon/package.json
	@cd $(JOBS_PATH)/neon_wrapper; \
		yarn install && \
		yarn build

$(JOBS_PATH)/pixel_wrapper/package.json:
	@cd $(JOBS_PATH); git clone --recurse-submodules -b develop https://github.com/DDMAL/pixel_wrapper.git

remote_jobs: $(JOBS_PATH)/pixel_wrapper/package.json $(JOBS_PATH)/neon_wrapper/static/editor.html
	@cd $(RODAN_PATH); $(REPLACE) "s/#py3 //g" ./settings.py
	@cd $(RODAN_PATH); $(REPLACE) "s/#gpu //g" ./settings.py

# Command Groups
clean_reset: stop clean build run
