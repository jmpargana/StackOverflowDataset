
help:
	cat Makefile

all: build run stop

build:
	docker-compose build

run:
	docker-compose up -d && docker wait scrapper_app && docker exec app mongoexport -d stackoverflowdataset -c stackoverflowdataset -o dataset.json --jsonArray && docker cp app:/dataset.json .

stop:
	docker stop scrapper_app app || true; docker rm scrapper_app app || true;

.PHONY: all
