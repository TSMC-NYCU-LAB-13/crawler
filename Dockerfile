FROM python:3.10-slim
COPY . /crawler
WORKDIR /crawler
RUN pip install -r ./requirements.txt
