# StackOverflowDataset

Using the python module **Scrapy**, create a dataset with certain stackoverflow
posts according to some given tags. This data will be processed in a short
deep learning project with AllenNLP.

## Usage

Build the docker container, run the web scrapper and export the mongodb
data to either csv or json.

!!Its not working yet!!

```sh
# to setup without mongo
docker build -t dataset .

# using docker compose
docker-compose up -d

# ssh into container
docker-compose exec app /bin/bash
```
