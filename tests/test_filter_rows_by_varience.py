import unittest
import pandas

from gen3va.heat_map_factory.filters import filter_rows_by_variance


class TestFilterRows(unittest.TestCase):

    def test_filter_rows(self):
        df = pandas.DataFrame(
            index=['a', 'b', 'c', 'd'],
            data=[
                [10, -5, 3],
                [4, 4, 4],
                [10, 1, -3],
                [-11, 0, 11]
            ]
        )

        answer = pandas.DataFrame(
            index=['a', 'd'],
            data=[[10, -5, 3],
                  [-11, 0, 11]]
        )

        df_filter = filter_rows_by_variance(df, 2)

        # Weird Pandas restriction: we can't compare DataFrames with the same
        # indices but in different orders. Ensure they're in the same order.
        # See : http://stackoverflow.com/questions/18548370/
        answer.sort_index(inplace=True)
        df_filter.sort_index(inplace=True)

        self.assertTrue((answer == df_filter).all().all())
