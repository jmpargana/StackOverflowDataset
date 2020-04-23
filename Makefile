
help:
	cat Makefile

build:
	docker-compose up -d

run:
	docker exec -d stackoverflowdataset_app_1 pipenv run python -m scrapy crawl sods

export:
	# this command isn't setup for docker yet
	# mongoexport -h localhost:27017 -d stackoverflowdataset -c stackoverflowdataset -o dataset.json -- jsonArray

stop:
	docker stop stackoverflowdataset_app_1 app || true; docker rm stackoverflowdataset_app_1 app || true;

