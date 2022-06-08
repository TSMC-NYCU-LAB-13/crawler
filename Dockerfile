FROM python:3.10-slim
COPY . /crawler
WORKDIR /crawler
RUN pip install -r ./requirements.txt
RUN apt-get update && apt-get install -y ca-certificates --no-install-recommends && rm -rf /var/lib/apt/lists/*
CMD [ "python", "/crawler/crawler.py" ]