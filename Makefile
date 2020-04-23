
help:
	cat Makefile

build:
	docker-compose up -d

run:
	docker exec -d scrapper_app pipenv run python -m scrapy crawl sods

export:
	# this command isn't setup for docker yet
	# mongoexport -h localhost:27017 -d stackoverflowdataset -c stackoverflowdataset -o dataset.json -- jsonArray

stop:
	docker stop scrapper_app app || true; docker rm scrapper_app app || true;

