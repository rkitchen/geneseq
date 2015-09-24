Installation
============

Dependencies
------------

### Docker ###
Follow these [instructions](https://docs.docker.com/installation/) to install docker on the host machine.

### Image ###
Run `docker pull miclaraia/geneseq`
to get the image. It might take a while as it's downloading some 500MB of data.

Running Docker
==============

Start the image by running:
```
docker run -i -t miclaraia/geneseq
```

To open a port to the application:
```
docker run -p 80:8080 miclaraia/geneseq
```

To open a port to mongo gui mongo-express:
```
docker run -p 8081 -i -t miclaraia/geneseq
```

To mount the database directory as a volume:
```
docker run -v ${host_directory}:/data -i -t miclaraia/geneseq
```

Putting it all together:
```
docker run -p 80:8080 -p 8081 -v {host_directory}:/data -i -t miclaraia/geneseq
```

Commands Inside Docker
======================

Supervisor
----------

To restart mongodb service:
```
supervisorctl restart mongo
```

To restart the python webserver:
```
supervisorctl restart uwsgi
```

To start and stop the mongo gui mongo-express
```
supervisorctl start mongo-express
supervisorctl stop mongo-express
```

Mongodb
-------

To restore a database from a compressed tar.gz mongodump, first
place the archive inside the host directory mounted to /data 
inside the docker container. Then run these commands:
```
cd /data
tar -zxvf {mongodump.tar.gz}
mongorestore --db dump/gene_locale gene_locale
```
Include the `--drop` option to mongorestore if a previous database exists
to ensure data integrity.

To dump a database, run this command:
```
mongodump --db gene-locale
```
This will create a directory `dump` in the current directory containing the 
database files. This is useful for creating periodic backups of the database
structure. Compress this dump by running:
```
tar -zcvf mongodump.tar.gz dump
```

Mongo Express
-------------

A utility which makes it easier to manage a mongo database. It 
also has the useful capability of editing single documents 
inside a databse. Start the service with supervisorctl and
make sure port 8081 is exposed in your docker instance.

### Configuration ###

Configuration file lives at /node_modules/mongo-express/config.js.
You can set the `username` and `password` fields here required to
access the service from a browser