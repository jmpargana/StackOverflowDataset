FROM python:3.8
WORKDIR /usr/src/app
COPY . ./
RUN pip3 install pipenv && pipenv install --skip-lock
CMD pipenv run python -m scrapy crawl sods
