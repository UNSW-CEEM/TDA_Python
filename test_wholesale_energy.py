import unittest
import wholesale_energy
import pandas as pd
from pandas.util.testing import assert_frame_equal


class TestGetFromTariffSet(unittest.TestCase):
    def setUp(self):
        # Test price data
        settlement_date = ["2018-01-01 00:00:00", "2018-01-01 00:30:00", "2018-01-01 01:00:00"]
        price = [100, 55, 67]
        self.price_data = pd.DataFrame.from_dict({'SETTLEMENTDATE': settlement_date,
                                                  'RRP': price})
        self.price_data['SETTLEMENTDATE'] = pd.to_datetime(self.price_data['SETTLEMENTDATE'])

        # Test load profiles
        one_profile = [1, 0.5, 7.27]
        second_profile = [11.4, -1, 8]
        date_time = ["2018-01-01 00:00:00", "2018-01-01 00:30:00", "2018-01-01 01:00:00"]
        self.load_profiles = pd.DataFrame.from_dict({'1': one_profile,
                                                     '2': second_profile})
        self.load_profiles.index = date_time
        self.load_profiles.index = pd.to_datetime(self.load_profiles.index)

        # Expected output
        annual_consumption = [sum(one_profile), 19.4]
        bill = [sum([a * b for a, b in zip(one_profile, price)])/1000,
                sum([a * b for a, b in zip(second_profile, price)])/1000]
        index = ['1', '2']
        self.expected_output = pd.DataFrame.from_dict({'Annual_kWh': annual_consumption,
                                                       'Bill': bill,
                                                       'Index': index})
        self.expected_output.set_index('Index', inplace=True)
        self.expected_output.index.name = None

    def test_wholesale_bills(self):
        calculated_answer = wholesale_energy.calc_wholesale_energy_costs(self.price_data, self.load_profiles)
        assert_frame_equal(calculated_answer, self.expected_output)
