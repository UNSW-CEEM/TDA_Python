import unittest
import format_case_for_export
import pandas as pd
from pandas.util.testing import assert_frame_equal


class TestAddingItem(unittest.TestCase):
    def testAddingItemToEmpty(self):
        empty = []
        name = 'just another project name'
        expected_result = [['project name', name]]
        data_to_save = format_case_for_export._add_single_item_with_label(
            data_for_export=empty, label='project name', item='just another project name')
        self.assertListEqual(data_to_save, expected_result, "Name adding to empty broken")

    def testAddingItemToNonEmpty(self):
        non_empty = [['random', 'pre-existing', 'data']]
        expected_result = [['random', 'pre-existing', 'data'], ['project name', 'just another project name']]
        data_to_save = format_case_for_export._add_single_item_with_label(
            data_for_export=non_empty, label='project name', item='just another project name')
        self.assertListEqual(data_to_save, expected_result, "Name adding to non empty broken")


class TestAddingDict(unittest.TestCase):
    def testAddingDictToNonEmpty(self):
        non_empty = [['random', 'pre-existing', 'data']]
        dict_to_add = {'year': 2017, 'state': 'NSW'}
        expected_result = [['random', 'pre-existing', 'data'],
                           ['wholsesale price source'],
                           ['year', 2017],
                           ['state', 'NSW']]
        data_to_save = format_case_for_export._add_one_level_dictionary(
            data_for_export=non_empty, label='wholsesale price source', dictionary=dict_to_add)
        self.assertListEqual(data_to_save, expected_result, "Dict adding to non empty broken")


class TestAddingDataFrame(unittest.TestCase):
    def testAddingDFToNonEmpty(self):
        non_empty = [['random', 'pre-existing', 'data']]
        customers = [1, 2, 5]
        bill = [11.4, -1, 8]
        usage = [100, 101, 103]
        dataframe = pd.DataFrame.from_dict({'CUSTOMER_KEY': customers, 'Bill': bill, 'Usage': usage})
        expected_result = [['random', 'pre-existing', 'data'],
                           ['CUSTOMER_KEY', 'Bill', 'Usage'],
                           [1, 11.4, 100],
                           [2, -1, 101],
                           [5, 8, 103]]
        data_to_save = format_case_for_export._add_results_dataframe(
            data_for_export=non_empty, dataframe=dataframe)
        self.assertListEqual(data_to_save, expected_result, "Dict adding to non empty broken")


class TestMergingResultDataFrames(unittest.TestCase):
    def testMergingWithDuplicateColumns(self):
        customers = [1, 2, 5]
        bill = [11.4, -1, 8]
        usage = [100, 101, 103]
        tuos_bill = [11.7, 11.9, 12]
        right_dataframe = pd.DataFrame.from_dict({'CUSTOMER_KEY': customers, 'Bill': bill, 'Usage': usage})
        left_dataframe = pd.DataFrame.from_dict({'CUSTOMER_KEY': customers, 'Bill': bill, 'Usage': usage,
                                                 'TUOS_Bill': tuos_bill})
        result_frame = format_case_for_export._merge_results_dataframes(left_dataframe, right_dataframe, "Retail",
                                                                        'Network')
        expected_dataframe = pd.DataFrame.from_dict({'CUSTOMER_KEY': customers, 'Bill_Retail': bill,
                                                     'Usage_Retail': usage, 'TUOS_Bill': tuos_bill,
                                                     'Bill_Network': bill, 'Usage_Network': usage})
        assert_frame_equal(result_frame, expected_dataframe)
