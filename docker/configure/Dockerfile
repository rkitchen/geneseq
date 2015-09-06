FROM geneseq:install-1.0
MAINTAINER Michael Laraia <micheal.laraia@gmail.com>

ENV MYSQL_USER=pipe \
    MYSQL_PASS=JcLAz2tpujdMnzsQ \
    MYSQL_SCHEMA=gene_locale \
    ON_CREATE_DB=gene_locale \
    REPLICATION_MASTER=**False** \
    REPLICATION_SLAVE=**False** \
    REPLICATION_USER=replica \
    REPLICATION_PASS=replica

COPY system_configs /

RUN /usr/local/bin/mysql_configure.sh && \
    mysql -u root gene_locale < /usr/local/bin/tables.sql

