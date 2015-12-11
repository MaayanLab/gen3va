"""Builds reports in the background.
"""

def build(tag):
    for sig in tag.gene_signatures:
        print(sig.extraction_id)
