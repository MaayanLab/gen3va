-- Create report table
CREATE TABLE IF NOT EXISTS `report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(255) NOT NULL,
  `report_type` varchar(255) NOT NULL,
  `tag_fk` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tag_fk` (`tag_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- Create foreign key relationship
ALTER TABLE `target_app_link` ADD `report_fk` INT NULL AFTER `gene_list_fk`, ADD INDEX (`report_fk`) ;

-- Create foreign key constraint.
ALTER TABLE `report` ADD FOREIGN KEY (`tag_fk`) REFERENCES `euclid`.`tag`(`id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `target_app_link` ADD FOREIGN KEY (`report_fk`) REFERENCES `euclid`.`report`(`id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Description for target_app_links
ALTER TABLE `target_app_link` ADD `description` TEXT NOT NULL AFTER `link`;

-- Create table for PCA visualizations
CREATE TABLE IF NOT EXISTS `pca_visualization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data` blob NOT NULL,
  `report_fk` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `report_fk` (`report_fk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- Create foreign key relationship
ALTER TABLE `pca_visualization` ADD FOREIGN KEY (`report_fk`) REFERENCES `euclid`.`report`(`id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

-- is_curated flag for tag table
ALTER TABLE `tag` ADD `is_curated` BOOLEAN NOT NULL AFTER `name`;