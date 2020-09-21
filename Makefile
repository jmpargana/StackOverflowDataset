
help:
	cat Makefile

all: build run export stop

build:
	docker-compose build

run:
	docker-compose up -d

plot:
	docker exec scrapper_app pipenv run python plotter/main.py && docker cp scrapper_app:/app/plot.html .

export:
	docker wait scrapper_app && docker exec mongo_app mongoexport -d stackoverflowdataset -c stackoverflowdataset -o dataset.json --jsonArray && docker cp mongo_app:/dataset.json .

stop:
	docker stop scrapper_app app || true; docker rm scrapper_app app || true;
