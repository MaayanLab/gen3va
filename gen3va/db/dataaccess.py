"""Handles most database transactions. It has knowledge of the primary classes
and their relationships and saves them accordingly.
"""

import sqlalchemy as sa

from substrate import GeneList, GeneSignature, GeoDataset, OptionalMetadata,\
    Report, SoftFile, Tag

from gen3va.db.utils import session_scope


def count(class_):
    """Returns the number of rows in an class's associated table.
    """
    with session_scope() as session:
        return session.query(class_).count()


def get(class_, value, key='id'):
    """Gets entity by comparing column to value.
    """
    with session_scope() as session:
        return session\
            .query(class_)\
            .filter(getattr(class_, key) == value)\
            .first()


def get_all(klass, session=None):
    """Gets all entities of a specific class.
    """
    if not session:
        with session_scope() as session:
            return session.query(klass).all()
    else:
        return session.query(klass).all()


def get_signatures_by_ids(extraction_ids):
    """Returns all gene signatures with matching extraction IDs.
    """
    with session_scope() as session:
        return session\
            .query(GeneSignature)\
            .filter(GeneSignature.extraction_id.in_(extraction_ids))\
            .all()


def get_statistics():
    """Returns object with DB statistics for about page.
    """
    with session_scope() as session:

        tags_dao = get_all(Tag)
        tags = []
        for tag in tags_dao:
            if len(tag.reports) == 0:
                report_status = 'inactive'
            else:
                report_status = tag.reports[-1].status

            tags.append({
                'name': tag.name,
                'is_curated': tag.is_curated,
                'report_status': report_status,
                'num_gene_signatures': len(tag.gene_signatures)
            })

        platforms = session.query(sa.func.distinct(GeoDataset.platform))
        platform_counts = []
        for tpl in platforms:
            platform = tpl[0]
            count = session.query(GeneSignature, SoftFile, GeoDataset)\
                .filter(SoftFile.dataset_fk == GeoDataset.id)\
                .filter(SoftFile.gene_signature_fk == GeneSignature.id)\
                .filter(GeoDataset.platform == platform)\
                .count()
            platform_counts.append({
                'platform': platform,
                'count': count
            })

        return {
            'num_gene_signatures': count(GeneSignature),
            'num_gene_lists': count(GeneList),
            'num_tags': count(Tag),
            'num_reports': count(Report),
            'num_platforms': len(platform_counts),
            'platform_counts': platform_counts,
            'tags': tags
        }