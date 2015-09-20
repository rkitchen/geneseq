FROM geneseq/install:latest
MAINTAINER Michael Laraia <micheal.laraia@gmail.com>

COPY system_configs /
ADD mongodump.tar.gz /data/dump

RUN /usr/local/bin/mongo_configure.sh && rm -R /mongodump