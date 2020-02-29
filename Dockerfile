
FROM python:3.9-slim-buster
LABEL maintainer="GoByte Developers <dev@gobyte.network>"
LABEL description="Dockerised GoByte Sentinel"

COPY . /sentinel