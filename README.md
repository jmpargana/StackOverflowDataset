# StackOverflowDataset

Using the python module **Scrapy**, create a dataset with certain stackoverflow
posts according to some given tags. This data will be processed in a short
deep learning project with AllenNLP.

## Usage

Build the docker container, run the web scrapper and export the mongodb
data to either csv or json.

```sh
make build
make run
```

Export dataset to JSON or CSV file.
```sh
mongoexport -h localhost:27017 -d stackoverflowdataset -c stackoverflowdataset -o dataset.json -- jsonArray
```
