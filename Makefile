include .env
export

##### Deploy #####

.PHONY: deploy-local
deploy-local: docker_image_cond
	docker-compose exec prefect-server /bin/bash -c 'cd /app/prefect/flows && python deployment_dev.py'

.PHONY: deploy-prod
deploy-prod: docker_image_cond
	docker compose exec prefect-server /bin/bash -c 'cd /app/prefect/flows && python deployment_prod.py'

.PHONY: deploy-prod-from-local
deploy-prod-from-local:
	ssh $(SSH_USER)@$(SSH_HOST) 'cd $(SSH_PATH_TO_PROJECT) && make git && sudo make deploy-prod'

##### Start & Stop App #####

.PHONY: start-app-prod
start-app-prod:
	./init_prod.sh start

.PHONY: stop-app-prod
stop-app-prod:
	./init_prod.sh stop 

.PHONY: start-app-local
start-app-local:
	./init_local.sh start; \
	export PREFECT_API_URL='http://0.0.0.0:4200/api/'; 
	
.PHONY: stop-app-local
stop-app-local:
	./init_local.sh stop 
	
.PHONY: restart-app-local
restart-app-local: stop-app-local start-app-local

.PHONY: restart-app-prod
restart-app-prod: stop-app-prod start-app-prod

##### Git #####

.PHONY: git
git:
	git fetch
	git pull


##### Copy env #####

.PHONY: copy-env-to-server
copy-env-to-server:
	@echo "Looking for .env files..."
	@files=$$(find . -name "*.env*" -type f); \
	echo "Found files:"; \
	select local_path in $$files; do \
		scp -i ~/.ssh/id_rsa $$local_path $(SSH_USER)@$(SSH_HOST):$(SSH_PATH_TO_PROJECT)/.env; \
		break; \
	done

##### SSH tunnels #####
.PHONY: ssh-tunnel-prefect
ssh-tunnel-prefect:
	ssh -i ~/.ssh/id_rsa -L 4200:localhost:4200 -N -f $(SSH_USER)@$(SSH_HOST)

.PHONY: ssh-tunnel-minio
ssh-tunnel-minio:
	ssh -i ~/.ssh/id_rsa -L 9001:localhost:9001 -N -f $(SSH_USER)@$(SSH_HOST)

.PHONY: find-running-tunnels
find-running-tunnels:
	ps aux | grep ssh