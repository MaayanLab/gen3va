import unittest
import pandas

from gen3va.heat_map_factory.filters import filter_rows_by_max_abs_val


class TestFilterRows(unittest.TestCase):

    def test_filter_rows(self):
        df = pandas.DataFrame(
            index=['a', 'b', 'c', 'd'],
            data=[
                [3, 3, 3],    # average: 3
                [-4, -4, -4], # average: -4
                [10, 1, -3],  # average: 2.66 -- should win
                [-11, 0, 11]  # average: 0    -- should win
            ]
        )

        answer = pandas.DataFrame(
            index=['c', 'd'],
            data=[[10, 1, -3],
                  [-11, 0, 11]]
        )

        df_filter = filter_rows_by_max_abs_val(df, 2)

        # Weird Pandas restriction: we can't compare DataFrames with the same
        # indices but in different orders. Ensure they're in the same order.
        # See : http://stackoverflow.com/questions/18548370/
        answer.sort_index(inplace=True)
        df_filter.sort_index(inplace=True)

        self.assertTrue((answer == df_filter).all().all())

    def test_filter_rows_negative(self):
        df = pandas.DataFrame(
            index=['a', 'b'],
            data=[
                [4, 4, 4], # average: 4
                [-9, 0, 0] # average: 0 -- should win
            ]
        )

        answer = pandas.DataFrame(
            index=['b'],
            data=[[-9, 0, 0]]
        )

        df_filter = filter_rows_by_max_abs_val(df, 1)
        answer.sort_index(inplace=True)
        df_filter.sort_index(inplace=True)

        self.assertTrue((answer == df_filter).all().all())
