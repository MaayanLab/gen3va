-- Create a resources foreign key on signature table.
-- CRITICAL: Set default resource_fk to 1, which should point to GEO. This means we don't have to redeploy GEO2Enrichr.
ALTER TABLE `gene_signature` ADD `resource_fk` INT NOT NULL DEFAULT '1' AFTER `extraction_id`;

-- Create resource table.
CREATE TABLE IF NOT EXISTS `resource` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

-- Load table
INSERT INTO `euclid`.`resource` (`id`, `code`, `name`) VALUES (NULL, 'geo', 'Gene Expression Omnibus');
INSERT INTO `euclid`.`resource` (`id`, `code`, `name`) VALUES (NULL, 'dtoxs', 'Drug Toxicity Signature Generation Center');

-- Set foreign key to GEO before beginning any data transactions.
UPDATE gene_signature SET resource_fk = 1;

-- Index and create foreign key
ALTER TABLE `gene_signature` ADD INDEX(`resource_fk`);
ALTER TABLE `gene_signature` ADD FOREIGN KEY (`resource_fk`) REFERENCES `euclid`.`resource`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

