#!/bin/bash
cd ~/Documents/Yale/server/docker
docker build -t geneseq/install:1.0 install && docker tag -f geneseq/install:1.0 geneseq/install:latest && \
docker build -t geneseq/configure:1.0 configure && docker tag -f geneseq/configure:1.0 geneseq/configure:latest && \
docker build --no-cache -t geneseq/code:1.0 code && docker tag -f geneseq/code:1.0 geneseq/code:latest && docker tag -f geneseq/code:1.0 miclaraia/geneseq:latest
