#!/bin/bash
cd ~/Documents/Yale/server/docker
cp ../pip_requirements.txt .
docker build -t miclaraia/geneseq:latest .
