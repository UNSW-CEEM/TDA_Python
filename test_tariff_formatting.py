import unittest
from tariff_processing import format_tariff_data_for_display, format_tariff_data_for_storage
from data_interface import get_tariffs


class TestConvertingTOU(unittest.TestCase):
    def setUp(self):
        self.storage_format = {'Date_accessed': '2018',
                               'Discount (%)': 0, 'Distributor': 'Essential Energy',
                               'Name': 'Essential Energy TOU NSW 2017/18',
                               'Parameters': {'DTUOS': {'Daily': {'Unit': '$/day', 'Value': 0.8568},
                                                        'Energy': {'Off Peak': {
                                                            'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                                            'TimeIntervals': {'T1': ['00:00', '07:00'],
                                                                              'T2': ['20:00', '24:00']},
                                                            'Unit': '$/kWh', 'Value': 0.043, 'Weekday': True,
                                                            'Weekend': False},
                                                                   'Off Peak - Weekend': {
                                                                       'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                                                       'TimeIntervals': {'T1': ['00:00', '24:00']},
                                                                       'Unit': '$/kWh', 'Value': 0.043,
                                                                       'Weekday': False, 'Weekend': True},
                                                                   'Peak-weekdays': {
                                                                       'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                                                       'TimeIntervals': {'T1': ['17:00', '20:00']},
                                                                       'Unit': '$/kWh', 'Value': 0.142, 'Weekday': True,
                                                                       'Weekend': False},
                                                                   'Shoulder-Weekdays': {
                                                                       'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                                                       'TimeIntervals': {'T1': ['07:00', '17:00']},
                                                                       'Unit': '$/kWh', 'Value': 0.1188,
                                                                       'Weekday': True, 'Weekend': False}}}},
                               'Provider': 'Essential Energy', 'ProviderType': 'Network', 'State': 'NSW',
                               'Tariff ID': 'TN0028', 'Type': 'TOU'}

        self.display_format = {'Date_accessed': '2018',
                               'Discount (%)': 0, 'Distributor': 'Essential Energy',
                               'Name': 'Essential Energy TOU NSW 2017/18',
                               'Parameters': {'DTUOS': {'Daily': {'table_header': ['Unit', 'Value'],
                                                                  'table_rows': [['$/day', '0.8568']]},
                                                        'Energy': {
                                                            'table_header': ['Name', 'Month', 'TimeIntervals',
                                                                             'Unit', 'Value', 'Weekday', 'Weekend'],
                                                            'table_rows': [['Off Peak',
                                                                            '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]',
                                                                            "{'T1': ['00:00', '07:00'], 'T2': ['20:00', '24:00']}",
                                                                            '$/kWh', '0.043', 'True', 'False'],
                                                                           ['Off Peak - Weekend',
                                                                            '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]',
                                                                            "{'T1': ['00:00', '24:00']}",
                                                                            '$/kWh', '0.043', 'False', 'True'],
                                                                           ['Peak-weekdays',
                                                                            '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]',
                                                                            "{'T1': ['17:00', '20:00']}",
                                                                            '$/kWh', '0.142', 'True', 'False'],
                                                                           ['Shoulder-Weekdays',
                                                                            '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]',
                                                                            "{'T1': ['07:00', '17:00']}",
                                                                            '$/kWh', '0.1188', 'True', 'False']
                                                                           ]}}},
                               'Provider': 'Essential Energy', 'ProviderType': 'Network', 'State': 'NSW',
                               'Tariff ID': 'TN0028', 'Type': 'TOU'}

    def test_storage_2_display(self):
        calculated_display_format = format_tariff_data_for_display(self.storage_format)
        self.assertDictEqual(self.display_format, calculated_display_format, "Display formatting failing for TOU tariff")

    def test_display_to_storage(self):
        calculated_storage_format = format_tariff_data_for_storage(self.display_format)
        self.assertDictEqual(self.storage_format, calculated_storage_format, "Storage formatting failing for TOU tariff")


class TestReversibleFormatting(unittest.TestCase):
    def setUp(self):
        self.network_tariffs = get_tariffs('network_tariff_selection_panel')
        self.retail_tariffs = get_tariffs('retail_tariff_selection_panel')

    def test_all_network_tariffs(self):
        for tariff in self.network_tariffs:
            calculated_display_format = format_tariff_data_for_display(tariff)
            calculated_storage_format = format_tariff_data_for_storage(calculated_display_format)
            self.assertDictEqual(tariff, calculated_storage_format,
                                 "Display formatting not reversible for {} tariff".format(tariff['Name']))

    def test_all_retail_tariffs(self):
        for tariff in self.retail_tariffs:
            calculated_display_format = format_tariff_data_for_display(tariff)
            calculated_storage_format = format_tariff_data_for_storage(calculated_display_format)
            self.assertDictEqual(tariff, calculated_storage_format,
                                 "Display formatting not reversible for {} tariff".format(tariff['Name']))

