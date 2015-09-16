#!/bin/bash

mkdir /data/db
/usr/local/bin/start_mongod.sh
mongorestore --db gene_locale /mongodump/dump/gene_locale