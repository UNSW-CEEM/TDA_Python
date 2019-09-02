import unittest
import format_chart_data_for_export
import pandas as pd
from pandas.util.testing import assert_frame_equal


class TestConvertingPlotlyFormatToPandas(unittest.TestCase):
    def testOneSeries(self):
        time_series = ['2017-01-01 00:00:00', '2017-01-01 00:30:00', '2017-01-01 01:30:00']
        a_y_series = [1, 2, 3]
        one_series = {'name': 'All', 'x': time_series, 'y': a_y_series}
        input_data_series = [one_series]
        input_data_set = {'chart_data': input_data_series, 'x_title': 'Time', 'y_title': 'Energy'}
        set_of_series_name = ['All', 'All', 'All']
        expected_dataframe = pd.DataFrame.from_dict({'Series': set_of_series_name,
                                                     'Time': time_series,
                                                     'Energy': a_y_series})
        result_frame = format_chart_data_for_export.plot_ly_to_pandas(input_data_set)
        assert_frame_equal(result_frame, expected_dataframe)

    def testTwoSeries(self):
        time_series = ['2017-01-01 00:00:00', '2017-01-01 00:30:00', '2017-01-01 01:30:00']
        a_y_series = [1, 2, 3]
        b_y_series = [1, 2, 3]
        one_series = {'name': 'a', 'x': time_series, 'y': a_y_series}
        two_series = {'name': 'b', 'x': time_series, 'y': a_y_series}
        input_data_series = [one_series, two_series]
        input_data_set = {'chart_data': input_data_series, 'x_title': 'Time', 'y_title': 'Energy'}
        set_of_series_name = ['a', 'a', 'a', 'b', 'b', 'b']
        expected_dataframe = pd.DataFrame.from_dict({'Series': set_of_series_name,
                                                     'Time': time_series + time_series,
                                                     'Energy': a_y_series + b_y_series})
        result_frame = format_chart_data_for_export.plot_ly_to_pandas(input_data_set)
        assert_frame_equal(result_frame, expected_dataframe)
