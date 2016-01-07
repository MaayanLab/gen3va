import unittest
import pandas

from gen3va.hierclust.filters import filter_rows_by_non_empty


class TestFilterRows(unittest.TestCase):

    def test_threshold_1(self):
        df = pandas.DataFrame(
            index=['a', 'b', 'c', 'd'],
            data=[
                [0, 0, 0],
                [1, 0, 1],
                [0, 0, 1],
                [1, 1, 1]
            ]
        )

        answer = pandas.DataFrame(
            index=['b', 'd'],
            data=[[1, 0, 1],
                  [1, 1, 1]]
        )
        df_filter = filter_rows_by_non_empty(df, 1)
        self.assertTrue((answer == df_filter).all().all())

    def test_threshold_2(self):
        df = pandas.DataFrame(
            index=['a', 'b', 'c', 'd'],
            data=[[0, 0, 0],
                  [1, 0, 1],
                  [0, 0, 1],
                  [1, 1, 1]]
        )

        answer = pandas.DataFrame(index=['d'],
                                  data=[[1, 1, 1]])
        df_filter = filter_rows_by_non_empty(df, 2)
        self.assertTrue((answer == df_filter).all().all())

    def test_negatives_real_numbers_etc(self):
        df = pandas.DataFrame(
            index=['a', 'b', 'c', 'd'],
            data=[[-0.5, 0, 0],
                  [0.1,  0, -0.2],
                  [5,    0, 1],
                  [9,    9, 9]]
        )

        answer = pandas.DataFrame(
            index=['b', 'c', 'd'],
            data=[[0.1,  0, -0.2],
                  [5,    0, 1],
                  [9,    9, 9]]
        )
        df_filter = filter_rows_by_non_empty(df)
        self.assertTrue((answer == df_filter).all().all())
