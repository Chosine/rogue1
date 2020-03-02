
FROM python:3.9-slim-buster
LABEL maintainer="GoByte Developers <dev@gobyte.network>"
LABEL description="Dockerised GoByte Sentinel"

COPY . /sentinel

RUN cd /sentinel && \
    rm sentinel.conf && \
    pip install -r requirements.txt

ENV HOME /sentinel
WORKDIR /sentinel

ADD share/run.sh /

CMD /run.sh