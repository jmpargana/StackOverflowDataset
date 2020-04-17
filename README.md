# StackOverflowDataset

Using the python module **Scrapy**, create a dataset with certain stackoverflow
posts according to some given tags. This data will be processed in a short
deep learning project with AllenNLP.

## Usage

!!Docker is still being setup!!

Build the docker container, run the web scrapper and export the mongodb
data to either csv or json.

```sh
# to setup without mongo
docker build -t dataset .

# using docker compose
docker-compose up -d

# ssh into container
docker-compose exec app /bin/bash
```

While docker is not ready

```sh
# prepare packages
pipenv install

# run bot
pipenv run python -m scrapy crawl sods
```

Export dataset to JSON or CSV file.
```sh
mongoexport -h localhost:27017 -d stackoverflowdataset -c stackoverflowdataset -o dataset.json -- jsonArray
```
