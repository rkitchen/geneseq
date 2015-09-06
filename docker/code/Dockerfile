FROM geneseq:configure-1.3
MAINTAINER Michael Laraia <micheal.laraia@gmail.com>

RUN git clone https://github.com/miclaraia/geneseq.git \ && chown -R http:http /usr/local/lib/geneseq
    /usr/local/lib/geneseq
RUN /usr/local/bin/start_mysqld.sh && \
    echo "LOAD DATA INFILE '/usr/local/lib/geneseq/data/processed.csv' INTO TABLE gene_locale.processed FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'" | \
    mysql -u root
