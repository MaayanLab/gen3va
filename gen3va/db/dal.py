"""Handles app-specific database transactions.
# """
#
# from substrate import Report, Tag
#
# from gen3va.db.util import session_scope
#
#
# def get_report(tag_name):
#     """Fetches report by tag name.
#     """
#     with session_scope() as session:
#         tag = session\
#             .query(Tag)\
#             .filter(Tag.name == tag_name)\
#             .first()
