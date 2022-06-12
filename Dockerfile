# TLS 1.3 force - https://stackoverflow.com/a/66936856
FROM python:3.10-slim
COPY . /crawler
WORKDIR /crawler
RUN pip install -r ./requirements.txt
RUN apt-get update && apt-get install -y ca-certificates --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN update-ca-certificates
CMD [ "python", "/crawler/crawler.py" ]