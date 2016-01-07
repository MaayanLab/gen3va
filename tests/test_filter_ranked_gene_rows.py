import unittest
import pandas

from gen3va.hierclust.clusterrankedgenes import _filter_highest_abs_val_mean_rows


class TestFilterRows(unittest.TestCase):

    def test_filter_rows(self):
        df = pandas.DataFrame(
            index=['a', 'b', 'c', 'd'],
            data=[
                [0, 0, 0],
                [1, 2, 1],
                [0, -4, 1],
                [1, 1, 1]
            ]
        )

        answer = pandas.DataFrame(
            index=['b', 'c'],
            data=[[1, 2, 1],
                  [0, -4, 1]]
        )
        df_filter = _filter_highest_abs_val_mean_rows(df, 2)
        self.assertTrue((answer == df_filter).all().all())

    def test_mean_not_variance(self):
        df = pandas.DataFrame(
            index=['a', 'b'],
            data=[
                [0, 0, 100],
                [34, 34, 34]
            ]
        )

        answer = pandas.DataFrame(
            index=['b'],
            data=[[34, 34, 34]]
        )
        df_filter = _filter_highest_abs_val_mean_rows(df, 1)
        self.assertTrue((answer == df_filter).all().all())
