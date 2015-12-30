-- Drop unnecessary data on target_app_link table
ALTER TABLE `target_app_link` DROP FOREIGN KEY `target_app_link_ibfk_3`;
ALTER TABLE `target_app_link` DROP `report_fk`;
ALTER TABLE `target_app_link` DROP `description`;

-- Create table for new hier_clust_visualization data.
CREATE TABLE IF NOT EXISTS `hier_clust_visualization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `link` text NOT NULL,
  `viz_type` varchar(255) NOT NULL,
  `enrichr_library` varchar(255) DEFAULT NULL,
  `report_fk` int(11) NOT NULL,
  `target_app_fk` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `target_app_fk` (`target_app_fk`),
  KEY `report_fk` (`report_fk`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=25 ;

-- Create foreign key constraints
ALTER TABLE `hier_clust_visualization` ADD FOREIGN KEY (`report_fk`) REFERENCES `euclid`.`report`(`id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `hier_clust_visualization` ADD FOREIGN KEY (`target_app_fk`) REFERENCES `euclid`.`target_app_link`(`id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Add descriptions for tag table.
ALTER TABLE `tag` ADD `description` TEXT NULL AFTER `is_curated`;

-- Descriptions for tag table.
UPDATE tag
  SET description = 'GEO has many studies where gene expression data from young human or mouse tissues was compared to old tissues. While these studies did not always focus on understanding the aging process, the data collected from them can be used to do so. Collecting signatures from young vs. old tissues can shed light on common alterations in pathway activity in aging and ultimately lead to the identification of small molecules that can potentially slow down aging. Note that the "young" samples are from mature but young adults and not from tissue collected from organisms that still undergo development and maturation.'
WHERE name = 'AGING_BD2K_LINCS_DCIC_COURSERA';

UPDATE tag
  SET description = 'MCF7 cells are a widely studied breast cancer cell line that is also profiled within the LINCS program by several assays and many perturbations. To complement the effort of the data collection of MCF7 by the LINCS consortium, the BD2K-LINCS DCIC is interested in accumulating gene expression signatures from prior studies that profiled gene expression before and after any perturbations of MCF7 cells. Such collection of signatures can be used to answer questions such as: how similar are MCF7 cells across labs and across platforms? Do perturbations of MCF7 cells converge into few prototypical responses?'
WHERE name = 'MCF7_BD2K_LINCS_DCIC_COURSERA';

UPDATE tag
  SET description = 'To complement the LINCS efforts to profile human cell responses to small molecule and gene knockdown perturbations, it is useful to have a collection of gene expression signatures collected from before and after treatment of human or mouse cells with endogenous ligands. Endogenous ligands are extracellular molecules that can be found in the body naturally. These ligands bind to receptors at the cell surface or can travel into the cell and bind to transcription factors. These small molecules signal to the cell about the status of the extracellular environment and whether the cell should take action and change its phenotypic behavior. Endogenous ligands include hormones such as growth factors, cytokines or chemokines.'
WHERE name = 'LIGANDS_BD2K_LINCS_DCIC_COURSERA';

UPDATE tag
  SET description = 'GEO has many studies where gene expression from human or mouse cells was collected before and after viral or bacterial infection of those cells. This collection of signatures can be used to potentially identify similarities between responses to different pathogens, and potentially help in identifying molecular mechanisms for novel pathogens based on their global molecular effects upon infection.'
WHERE name = 'PATHOGENS_BD2K_LINCS_DCIC_COURSERA';

