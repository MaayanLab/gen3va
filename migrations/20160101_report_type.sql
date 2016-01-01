-- Rename report_type default from "tag" to "default"
UPDATE `report`
  SET `report`.`report_type` = "default";