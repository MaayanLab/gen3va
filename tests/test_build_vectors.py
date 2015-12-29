import unittest

from gen3va.core.hierclust.utils import build_vectors

def _in(lst, tpl):
    for t in lst:
        if tpl[0] == t[0] and tpl[1] == t[1]:
            return True
    return False


class TestSumPerturbations(unittest.TestCase):

    """
    # Input
    A = [['A',1], ['B',1], ['C',1], ['D',1]]
    B = [['C',-1], ['D',-1], ['E',-1], ['F',-1]]

    # Output
    A  = [['A',1], ['B',1], ['C',1],  ['D',1],  ['E',0],  ['F',0]]
    B  = [['A',0], ['B',0], ['C',-1], ['D',-1], ['E',-1], ['F',-1]]
    AB = [['A',1], ['B',1], ['C',0],  ['D',0],  ['E',-1], ['F',-1]]
    """

    def test_overlapping_sets(self):
        up, down, combined = build_vectors(
            {'A': 1, 'B': 1, 'C': 1, 'D': 1},
            {'C': -1, 'D': -1, 'E': -1, 'F': -1}
        )

        # Up
        self.assertTrue(_in(up, ['A', 1]))
        self.assertTrue(_in(up, ['B', 1]))
        self.assertTrue(_in(up, ['C', 1]))
        self.assertTrue(_in(up, ['D', 1]))
        self.assertTrue(_in(up, ['E', 0]))
        self.assertTrue(_in(up, ['F', 0]))

        # Down
        self.assertTrue(_in(down, ['A', 0]))
        self.assertTrue(_in(down, ['B', 0]))
        self.assertTrue(_in(down, ['C', -1]))
        self.assertTrue(_in(down, ['D', -1]))
        self.assertTrue(_in(down, ['E', -1]))
        self.assertTrue(_in(down, ['F', -1]))

        # Combined
        self.assertTrue(_in(combined, ['A', 1]))
        self.assertTrue(_in(combined, ['B', 1]))
        self.assertTrue(_in(combined, ['C', 0]))
        self.assertTrue(_in(combined, ['D', 0]))
        self.assertTrue(_in(combined, ['E', -1]))
        self.assertTrue(_in(combined, ['F', -1]))

    def test_no_sets_with_no_overlap(self):
        up, down, combined = build_vectors(
            {'A': 1, 'B': 1},
            {'C': -1, 'D': -1}
        )

        # Up
        self.assertTrue(_in(up, ['A', 1]))
        self.assertTrue(_in(up, ['B', 1]))
        self.assertTrue(_in(up, ['C', 0]))
        self.assertTrue(_in(up, ['D', 0]))

        # Down
        self.assertTrue(_in(down, ['A', 0]))
        self.assertTrue(_in(down, ['B', 0]))
        self.assertTrue(_in(down, ['C', -1]))
        self.assertTrue(_in(down, ['D', -1]))

        # Combined
        self.assertTrue(_in(combined, ['A', 1]))
        self.assertTrue(_in(combined, ['B', 1]))
        self.assertTrue(_in(combined, ['C', -1]))
        self.assertTrue(_in(combined, ['D', -1]))

    def test_with_doubles(self):
        up, down, combined = build_vectors(
            {'A': 0.5, 'B': 0.7, 'C': 0.85},
            {'C': -0.41, 'D': -1, 'E': -0.3}
        )

        # Up
        self.assertTrue(_in(up, ['A', 0.5]))
        self.assertTrue(_in(up, ['B', 0.7]))
        self.assertTrue(_in(up, ['C', 0.85]))
        self.assertTrue(_in(up, ['D', 0]))
        self.assertTrue(_in(up, ['E', 0]))

        # Down
        self.assertTrue(_in(down, ['A', 0]))
        self.assertTrue(_in(down, ['B', 0]))
        self.assertTrue(_in(down, ['C', -0.41]))
        self.assertTrue(_in(down, ['D', -1]))
        self.assertTrue(_in(down, ['E', -0.3]))

        # Combined
        self.assertTrue(_in(combined, ['A', 0.5]))
        self.assertTrue(_in(combined, ['B', 0.7]))
        self.assertTrue(_in(combined, ['C', 0.44]))
        self.assertTrue(_in(combined, ['D', -1]))
        self.assertTrue(_in(combined, ['E', -0.3]))