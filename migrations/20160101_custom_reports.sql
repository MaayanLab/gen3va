-- Rename report_type default from "tag" to "default"
UPDATE `report`
  SET `report`.`report_type` = "default";

-- Rename join tables for consistency.
RENAME TABLE `ranked_gene_2_gene_list` TO `ranked_gene_to_gene_list`;
RENAME TABLE `gene_signatures_to_tags` TO `gene_signature_to_tag`;

-- Join table for linking reports to gene signatures
CREATE TABLE IF NOT EXISTS `gene_signature_to_report` (
  `gene_signature_fk` int(11) NOT NULL,
  `report_fk` int(11) NOT NULL,
  KEY `gene_signature_fk` (`gene_signature_fk`,`report_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;