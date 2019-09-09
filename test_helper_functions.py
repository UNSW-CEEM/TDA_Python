import unittest
import helper_functions
import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np


class TestAddMissingCustomerKeysToDemoFile(unittest.TestCase):
    def testLoadHasExtraKey(self):
        keys_demo_file = ['1', '2', '3']
        has_air_con = ['Y', 'Y', 'N']
        coolness_factor = [1.0, 2.0, 68.9]
        demo_file = pd.DataFrame.from_dict({'CUSTOMER_KEY': keys_demo_file, 'HASAIR': has_air_con,
                                            'COOLNESS': coolness_factor})
        one_profile = [1, 0.5, 7.27]
        second_profile = [11.4, -1, 8]
        date_time = ["2018-01-01 00:00:00", "2018-01-01 00:30:00", "2018-01-01 01:00:00"]
        load_profiles = pd.DataFrame.from_dict({'Datetime': date_time,
                                                '1': one_profile,
                                                '2': second_profile,
                                                '3': second_profile,
                                                '4': second_profile})
        load_profiles['Datetime'] = pd.to_datetime(load_profiles['Datetime'])
        keys_demo_file = ['1', '2', '3', '4']
        has_air_con = ['Y', 'Y', 'N', np.nan]
        coolness_factor = [1.0, 2.0, 68.9, np.nan]
        expected_df = pd.DataFrame.from_dict({'CUSTOMER_KEY': keys_demo_file, 'HASAIR': has_air_con,
                                              'COOLNESS': coolness_factor})
        answer = helper_functions.add_missing_customer_keys_to_demo_file_with_nan_values(load_profiles, demo_file)
        assert_frame_equal(answer, expected_df)

    def testLoadHasMissingKey(self):
        keys_demo_file = ['1', '2', '3']
        has_air_con = ['Y', 'Y', 'N']
        coolness_factor = [1.0, 2.0, 68.9]
        demo_file = pd.DataFrame.from_dict({'CUSTOMER_KEY': keys_demo_file, 'HASAIR': has_air_con,
                                            'COOLNESS': coolness_factor})
        one_profile = [1, 0.5, 7.27]
        second_profile = [11.4, -1, 8]
        date_time = ["2018-01-01 00:00:00", "2018-01-01 00:30:00", "2018-01-01 01:00:00"]
        load_profiles = pd.DataFrame.from_dict({'Datetime': date_time,
                                                '1': one_profile,
                                                '2': second_profile})
        load_profiles['Datetime'] = pd.to_datetime(load_profiles['Datetime'])
        keys_demo_file = ['1', '2', '3']
        has_air_con = ['Y', 'Y', 'N']
        coolness_factor = [1.0, 2.0, 68.9]
        expected_df = pd.DataFrame.from_dict({'CUSTOMER_KEY': keys_demo_file, 'HASAIR': has_air_con,
                                              'COOLNESS': coolness_factor})
        answer = helper_functions.add_missing_customer_keys_to_demo_file_with_nan_values(load_profiles, demo_file)
        assert_frame_equal(answer, expected_df)



