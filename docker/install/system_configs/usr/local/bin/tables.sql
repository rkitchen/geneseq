CREATE TABLE `processed` (
  `celltype` varchar(30) DEFAULT NULL,
  `expression` float DEFAULT NULL,
  `expression_next` float DEFAULT NULL,
  `geneID` varchar(30) DEFAULT NULL,
  `geneName` varchar(20) DEFAULT NULL,
  `geneType` varchar(20) DEFAULT NULL,
  `geneStatus` varchar(10) DEFAULT NULL,
  `geneID_human_gencode21` varchar(30) DEFAULT NULL,
  `geneID_human` varchar(30) DEFAULT NULL,
  `geneID_mouse` varchar(30) DEFAULT NULL,
  `identity` smallint(6) DEFAULT NULL,
  `confidence` float DEFAULT NULL,
  `geneID_expressionMatrixID` varchar(45) DEFAULT NULL,
  `WGCNAModuleID` varchar(10) DEFAULT NULL,
  KEY `SEARCH` (`geneName`)
) ENGINE=InnoDB AUTO_INCREMENT=1125 DEFAULT CHARSET=utf8;
