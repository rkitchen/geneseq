#!/bin/bash
cd ~/Documents/Yale/server/docker
docker build -t geneseq/install:1.0 install && docker tag -f geneseq/code:1.0 miclaraia/geneseq:latest
