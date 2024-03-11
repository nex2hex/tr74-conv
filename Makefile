build:
	docker stop conv
	docker rm conv
	docker build . -t conv
	docker create --name conv \
		--mount type=bind,source="$(shell pwd)",target=/code \
		-u $(shell id -u ${USER}):$(shell id -g ${USER}) \
		-p 8080:80 \
		-it conv

build_prod:
	docker rm conv_prod
	docker build . -t conv_prod -f Dockerfile_prod

remove:
	docker stop conv
	docker rm conv

shell:
	docker start conv
	docker exec -it conv /bin/bash

stop:
	docker stop conv

python:
	docker exec -it conv /usr/local/bin/python3

runserver:
	docker start conv
	docker exec -it conv sh -c "uvicorn app.main:app --host 0.0.0.0 --port 80"