"""
"""


TYPES = []


def cluster(extraction_ids, report, back_link, **kwargs):
    pass



# def from_enriched_terms(extraction_ids=None,
#                         background_type='ChEA_2015',
#                         report=None,
#                         back_link=''):
#     if extraction_ids:
#         gene_signatures = []
#         for extraction_id in extraction_ids:
#             gene_signature = dataaccess.get_gene_signature(extraction_id)
#             gene_signatures.append(gene_signature)
#     else:
#         gene_signatures = report.get_gene_signatures()
#     return __from_enriched_terms(gene_signatures, background_type, back_link)