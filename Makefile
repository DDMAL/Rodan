# TODO: Some of these should be converted into Ansible Playbooks when there's time.

# Chose a makefile because its easier to read over a bunch of if statements inside a bash script.
# We are taking advantage of .PHONY that is available in makefiles to create this simple looking
# list of command shortcuts

# Portable replacement for `sed` or `gsed`
# See https://unix.stackexchange.com/questions/92895/how-can-i-achieve-portability-with-sed-i-in-place-editing
REPLACE := perl -i -pe

RODAN_PATH := ./rodan-main/code/rodan
JOBS_PATH := $(RODAN_PATH)/jobs

PROD_TAG := v2.0.0

# Individual Commands

build:
	@echo "[-] Rebuilding Docker Images for Rodan..."
	# Build py2-celery, because it's needed for Rodan and Celery images
	# @docker-compose -f build.yml build --no-cache py2-celery # Sometimes it's better to use the
	# 	no-cache option if something unexplicably broke with the py2-celery image (a cached build step perhaps)
	@docker-compose -f build.yml build --no-cache py2-celery
	# Build rodan and rodan-client because they are needed for nginx
	@docker-compose -f build.yml build --no-cache --parallel rodan rodan-client
	# DockerHub is not intuitive. You won't be able to build from the source root folder in both build contextes.
	# When you build locally, the COPY command is relative to the dockerfile. When you build on DockerHub, its relative to the source root.
	# For this reason we replace the name to build locally because we build more often on DockerHub than on local.
	@$(REPLACE) "s/COPY .\/postgres\/maintenance/COPY .\/maintenance/g" ./postgres/Dockerfile || $(REPLACE) "s/COPY .\/postgres\/maintenance/COPY .\/maintenance/g" ./postgres/Dockerfile
	@docker-compose -f build.yml build --no-cache --parallel nginx py3-celery gpu-celery postgres hpc-rabbitmq
	# Revert back the change to the COPY command so it will work on Docker Hub.
	@$(REPLACE) "s/COPY .\/maintenance/COPY .\/postgres\/maintenance/g" ./postgres/Dockerfile || $(REPLACE) "s/COPY .\/maintenance/COPY .\/postgres\/maintenance/g" ./postgres/Dockerfile
	@echo "[+] Done."

backup_db:
	@docker exec `docker ps -f name=rodan_postgres -q` backup

restore_db:
	@docker exec `docker ps -f name=rodan_postgres -q` restore

# Keep in mind, you may need to deal with the postgres/maintenance/backup or backups files depending on setup

run: remote_jobs
	# Run local version for dev
	# Hello, 2022 hires!
	@docker-compose up

test_prod: pull_prod 
	# Test production Rodan images with specified tag
	# May want to change test-prod-compose.yml if you want a 
	# different tag.
	docker-compose -f test-prod-compose.yml up

build_arm:
	@docker build -f ./nginx/Dockerfile.arm --no-cache --tag nginx-local nginx

run_arm:
	# Run build_arm first if you don't have the NGINX container.
	# Launch ARM instance 
	@docker-compose -f arm-compose.yml up

run_client:
	# Run Rodan-Client for dev (needs local dev up and running)
	@docker run -p 8080:9002 -v `pwd`/rodan-client/code:/code ddmal/rodan-client:nightly bash

deploy_staging:
	# Can also be used to update a configuration (point to a different image.)
	@echo "[-] Deploying Docker Swarm for: Rodan Staging"
	@docker stack deploy --prune --with-registry-auth -c staging.yml rodan
	@echo "[+] Done."

deploy_production:
	# Can also be used to update a configuration (point to a different image.)
	@echo "[-] Deploying Docker Swarm for: Rodan Production"
	@docker stack deploy --with-registry-auth -c production.yml rodan
	@echo "[+] Done."

copy_docker_tag:
	# tag=v1.5.0rc0 make copy_docker_tag
	@docker image tag $(docker images ddmal/rodan:nightly -q) ddmal/rodan:$(tag)
	@docker image tag $(docker images ddmal/rodan-python2-celery:nightly -q) ddmal/rodan-python2-celery:$(tag)
	@docker image tag $(docker images ddmal/rodan-python3-celery:nightly -q) ddmal/rodan-python3-celery:$(tag)
	@docker image tag $(docker images ddmal/rodan-gpu-celery:nightly -q) ddmal/rodan-gpu-celery:$(tag)

pull_prod:
	docker pull ddmal/hpc-rabbitmq:$(PROD_TAG)
	docker pull ddmal/iipsrv:nightly
	docker pull ddmal/nginx:$(PROD_TAG)
	docker pull ddmal/postgres-plpython:$(PROD_TAG)
	docker pull ddmal/rodan-gpu-celery:$(PROD_TAG)
	docker pull ddmal/rodan-main:$(PROD_TAG)
	docker pull ddmal/rodan-python2-celery:$(PROD_TAG)
	docker pull ddmal/rodan-python3-celery:$(PROD_TAG)
	docker pull rabbitmq:alpine
	docker pull redis:alpine

pull_docker_tag:
	# tag=v1.5.0rc0 make pull_docker_tag
	@docker pull ddmal/rodan:$(tag)
	@docker pull ddmal/rodan-python2-celery:$(tag)
	@docker pull ddmal/rodan-python3-celery:$(tag)
	@docker pull ddmal/rodan-gpu-celery:$(tag)

push_docker_tag:
	# tag=v1.5.0rc0 make push_docker_tag
	@docker push ddmal/rodan:$(tag)
	@docker push ddmal/rodan-python2-celery:$(tag)
	@docker push ddmal/rodan-python3-celery:$(tag)
	@docker push ddmal/rodan-gpu-celery:$(tag)

update:
	# tag1=v1.5.0rc0 tag2=v1.3.1 make update
	# This will update the nightly images forcefully
	@echo "[-] Updating Docker Swarm images..."
	# @docker-compose pull

	# DB First
	@docker service update \
		--force \
		--update-order start-first \
		--update-delay 30s \
		--image ddmal/postgres-plpython:$(tag2) \
		rodan_postgres 
	
	# You need to be logged in to docker for this one.
	@docker service update \
		--force \
		--with-registry-auth \
		--update-order start-first \
		--update-delay 10m \
		--image ddmal/rodan:$(tag1) \
		rodan_rodan-main

	# These images might need time to update.
	@docker service update \
		--force \
		--with-registry-auth \
		--update-order start-first \
		--stop-grace-period 9h \
		--update-delay 10m \
		--image ddmal/rodan:$(tag1) \
		rodan_celery
	# These are public images
	@docker service update \
		--force \
		--update-order start-first \
		--stop-grace-period 9h \
		--update-delay 30s \
		--image ddmal/rodan-python2-celery:$(tag1) \
		rodan_py2-celery
	@docker service update \
		--force \
		--update-order start-first \
		--stop-grace-period 9h \
		--update-delay 30s \
		--image ddmal/rodan-python3-celery:$(tag1) \
		rodan_py3-celery
	@docker service update \
		--force \
		--update-order start-first \
		--stop-grace-period 9h \
		--update-delay 30s \
		--image ddmal/rodan-gpu-celery:$(tag1) \
		rodan_gpu-celery

	# # TODO: Need to make rabbitmq durable and permanent
	# # before we can make rolling updates for rabbitmq/hpc-rabbitmq.
	# @docker service update \
	# 	--force \
	# 	--update-order start-first \
	# 	--update-delay 30s \
	# 	--image ddmal/hpc-rabbitmq:$(tag2) \
	# 	rodan_hpc-rabbitmq
	@docker service update \
		--force \
		--update-order start-first \
		--update-delay 30s \
		--image ddmal/nginx:$(tag2) \
		rodan_nginx

	@echo "[+] Done."

scale:
	@docker service scale rodan_nginx=$(num)
	@docker service scale rodan_rodan=$(num)
	@docker service scale rodan_celery=$(num)
	@docker service scale rodan_py2-celery=$(num)
	@docker service scale rodan_py3-celery=$(num)
	# @docker service scale rodan_gpu-celery=$(num)
	@docker service scale rodan_redis=$(num)
	# @docker service scale rodan_postgres=$(num)
	@docker service scale rodan_rabbitmq=$(num)
	@docker service scale rodan_hpc-rabbitmq=$(num)

health:
	@docker inspect --format "{{json .State.Health }}" $(log) | jq

renew_certbot:
	@docker exec `docker ps -f name=rodan_nginx -q` certbot renew --no-random-sleep-on-renew
	@docker exec `docker ps -f name=rodan_nginx -q` nginx -s reload

stop:
	# This is the same command to stop docker swarm or docker-compose
	@echo "[-] Stopping all running docker containers and services..."
	@docker service rm `docker service ls -q` >>/dev/null 2>&1 || echo "[+] No Services Running"
	@docker stop `docker ps -aq` >>/dev/null 2>&1 || echo "[+] No Containers Running"
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


clean_swarm:
	# Not usually needed, but this will restart the swarm
	@echo "[-] Exiting from Docker Swarm and recreating new Swarm Manager..."
	@docker stack rm rodan || echo "[-] No stack to remove"
	@docker swarm leave --force || echo "[-] Not a swarm manager"
	@docker swarm init
	@echo "[+] Done."

debug_swarm:
	@echo "[+] Creating a live service in the same network."
	@docker service create --name statefulservice --network rodan_default --entrypoint="bash -c 'tail -f /dev/null'" --env-file=./scripts/staging.env ddmal/rodan:nightly bash
	@docker exec -it `docker ps -f name=statefulservice -q` bash

push:
	@echo "[-] Pushing images to Docker Hub..."
	@docker-compose push
	@echo "[+] Done."

pull:
	@echo "[-] Pulling docker images from Docker Hub..."
	@docker-compose pull
	@echo "[+] Done."

$(JOBS_PATH)/neon_wrapper/Neon/package.json:
	@cd $(JOBS_PATH); \
		git clone --recurse-submodules -b neon_v5 https://github.com/DDMAL/neon_wrapper.git

$(JOBS_PATH)/neon_wrapper/static/editor.html: $(JOBS_PATH)/neon_wrapper/Neon/package.json
	@cd $(JOBS_PATH)/neon_wrapper; \
		yarn install && \
		yarn build

$(JOBS_PATH)/pixel_wrapper/package.json:
	@cd $(JOBS_PATH); git clone --recurse-submodules -b develop https://github.com/DDMAL/pixel_wrapper.git

remote_jobs: $(JOBS_PATH)/pixel_wrapper/package.json $(JOBS_PATH)/neon_wrapper/static/editor.html 
	@cd $(RODAN_PATH); $(REPLACE) "s/#py2 //g" ./settings.py
	@cd $(RODAN_PATH); $(REPLACE) "s/#py3 //g" ./settings.py
	@cd $(RODAN_PATH); $(REPLACE) "s/#gpu //g" ./settings.py

# Command Groups
reset: stop clean pull run
clean_reset: stop clean build run
upload: clean_reset push
deploy: clean_git pull run_swarm
reset_swarm: stop clean_git clean_swarm clean pull deploy_staging
update_swarm: clean_git update
staging: stop clean pull deploy_staging