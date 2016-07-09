-- We need to force GEN3VA to re-fetch all enrichr results.
DELETE FROM enrichr_result;

-- We need to save the Enrichr library with the results now.
ALTER TABLE enrichr_result
ADD library VARCHAR(255);

-- Create enrichment_term table
CREATE TABLE enrichment_term (
  id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  combined_score DOUBLE,
  rank INT,
  enrichr_result_fk INT
);

-- Create perturbation table
CREATE TABLE perturbation (
  id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  score DOUBLE,
  rank INT,
  l1000cds2_result_fk INT
);

-- Add foreign keys
ALTER TABLE enrichment_term
ADD CONSTRAINT fk_enrichr_result FOREIGN KEY (enrichr_result_fk)
REFERENCES enrichr_result (id)
ON DELETE CASCADE;

-- Add foreign keys
ALTER TABLE perturbation
ADD CONSTRAINT fk_l1000cds2_result FOREIGN KEY (l1000cds2_result_fk)
REFERENCES enrichr_result (id)
ON DELETE CASCADE;
