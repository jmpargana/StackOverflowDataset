# StackOverflowDataset

[![Build Status](https://travis-ci.org/jmpargana/StackOverflowDataset.svg?branch=master)](https://travis-ci.org/jmpargana/StackOverflowDataset)
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

StackOverflowDataset contains two python scripts, one using the [Scrapy](https://scrapy.org) framework to extract all questions available on [stackoverflow](htts://stackoverflow.com) and the other to plot a three dimensional network graph of
the top tags used and their relationship to each other.
The package is implemented in a [docker](https://docker.com) environment that 
will silently run both scripts and copy the resulting data to a *json* file as well
as the plot to an *html* file.

## Usage

To run the scripts just build the container and run it with the two commands:

```sh
make build
make run
```

You can generate a plot at any time with the already fetched data
which will be saved in the *plot.html* file and exported
to the current directory by using the command:

```sh
make plot
```

Additionally you can wait until the fetching script is done (this might take several hours, since stackoverflow has 20M+ questions) and export both the *json* as well
as the *html* file.

```sh
make export
```

And finally you can clean the environment by deleting the docker containers and
volume by typing:

```sh
make stop
```

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

- **[MIT License](LICENSE)**
- Copyright 2020 João Pargana
