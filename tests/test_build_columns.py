import unittest
import pandas

from gen3va.heat_map_factory.utils import build_columns

def _in(lst, tpl):
    for t in lst:
        if tpl[0] == t[0] and tpl[1] == t[1]:
            return True
    return False


class TestBuildColumns(unittest.TestCase):

    """
    # Conceptual input
    A = [('A',1),  ('B',1],  ('C',1),  ('D',1)]
    B = [('C',-1), ('D',-1), ('E',-1), ('F',-1)]

    # Conceptual output
    A  = [('A',1), ('B',1), ('C',1),  ('D',1),  ('E',0),  ('F',0)]
    B  = [('A',0), ('B',0), ('C',-1), ('D',-1), ('E',-1), ('F',-1)]
    AB = [('A',1), ('B',1), ('C',0),  ('D',0),  ('E',-1), ('F',-1)]
    """

    def test_overlapping_sets(self):
        mimic = pandas.Series(index=['A', 'B', 'C', 'D'], data=[1, 1, 1, 1])
        reverse = pandas.Series(index=['C', 'D', 'E', 'F'], data=[-1, -1, -1, -1])
        answer = [
            {
                'row_name': 'A',
                'val': 1,
                'val_up': 1,
                'val_dn': 0
            },
            {
                'row_name': 'B',
                'val': 1,
                'val_up': 1,
                'val_dn': 0
            },
            {
                'row_name': 'C',
                'val': 0,
                'val_up': 1,
                'val_dn': -1
            },
            {
                'row_name': 'D',
                'val': 0,
                'val_up': 1,
                'val_dn': -1
            },
            {
                'row_name': 'E',
                'val': -1,
                'val_up': 0,
                'val_dn': -1
            },
            {
                'row_name': 'F',
                'val': -1,
                'val_up': 0,
                'val_dn': -1
            }
        ]
        column_data = build_columns(mimic, reverse)
        self.assertTrue(column_data == answer)

    def test_no_sets_with_no_overlap(self):
        mimic = pandas.Series(index=['A', 'B'], data=[1, 1])
        reverse = pandas.Series(index=['E', 'F'], data=[-1, -1])
        answer = [
            {
                'row_name': 'A',
                'val': 1,
                'val_up': 1,
                'val_dn': 0
            },
            {
                'row_name': 'B',
                'val': 1,
                'val_up': 1,
                'val_dn': 0
            },
            {
                'row_name': 'E',
                'val': -1,
                'val_up': 0,
                'val_dn': -1
            },
            {
                'row_name': 'F',
                'val': -1,
                'val_up': 0,
                'val_dn': -1
            }
        ]
        column_data = build_columns(mimic, reverse)
        self.assertTrue(column_data == answer)

    def test_with_doubles(self):
        mimic = pandas.Series(index=['A', 'B', 'C'], data=[0.5, 0.7, 0.85])
        reverse = pandas.Series(index=['C', 'D', 'E'], data=[-0.41, -1, -0.3])
        answer = [
            {
                'row_name': 'A',
                'val': 0.5,
                'val_up': 0.5,
                'val_dn': 0
            },
            {
                'row_name': 'B',
                'val': 0.7,
                'val_up': 0.7,
                'val_dn': 0
            },
            {
                'row_name': 'C',
                'val': 0.44,
                'val_up': 0.85,
                'val_dn': -0.41
            },
            {
                'row_name': 'D',
                'val': -1,
                'val_up': 0,
                'val_dn': -1
            },
            {
                'row_name': 'E',
                'val': -0.3,
                'val_up': 0,
                'val_dn': -0.3
            }
        ]
        column_data = build_columns(mimic, reverse)
        self.assertTrue(column_data == answer)
