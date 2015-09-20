LOAD DATA INFILE '/usr/local/lib/geneseq/data/processed.csv'
    INTO TABLE gene_locale.processed
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n';
ALTER TABLE gene_locale.processed
    ADD COLUMN `id` INT NOT NULL AUTO_INCREMENT FIRST,
    ADD PRIMARY KEY (`id`),
    ADD UNIQUE INDEX `id_UNIQUE` (`id` ASC);