-- Drop old columns
ALTER TABLE `tag` DROP `description`;
ALTER TABLE `tag` DROP `is_curated`;

-- Add new foreign key column
ALTER TABLE `tag` ADD `curator_fk` INT NOT NULL AFTER `name`;

-- Create table for curators, such as Coursera NSAB, Harmonizome, etc.
CREATE TABLE IF NOT EXISTS `curator` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;