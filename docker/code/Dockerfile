FROM geneseq/configure:latest
MAINTAINER Michael Laraia <micheal.laraia@gmail.com>

RUN  git clone https://github.com/miclaraia/geneseq.git \
    /usr/local/lib/geneseq && \
    chown -R http:http /usr/local/lib/geneseq
RUN /usr/local/bin/start_mysqld.sh && \
    mysql -u root < /usr/local/bin/import_csv.sql

EXPOSE 8080
ENTRYPOINT /bin/bash -c "/usr/local/bin/startup.sh; /bin/bash"
