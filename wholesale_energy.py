from nemosis import data_fetch_methods
import pandas as pd
import numpy as np


def get_wholesale_prices(year, region):
    start_time = "{}/01/01 00:00:00".format(year,)
    end_time = "{}/01/01 00:00:00".format(int(year,) + 1)
    table = "TRADINGPRICE"
    raw_data_cache = 'data/aemo_raw_cache/'
    price_data = data_fetch_methods.dynamic_data_compiler(start_time, end_time, table, raw_data_cache)
    price_data = price_data[price_data['REGIONID'] == (region + '1')]
    price_data = price_data.loc[:, ['SETTLEMENTDATE', 'RRP']]
    price_data['RRP'] = pd.to_numeric(price_data['RRP'])
    price_data['SETTLEMENTDATE'] = pd.to_datetime(price_data['SETTLEMENTDATE'])
    return price_data


def calc_wholesale_energy_costs(price_data, load_profiles):

    imports = [np.nansum(load_profiles[col].values[load_profiles[col].values > 0])
               for col in load_profiles.columns if col != 'Datetime']
    results = pd.DataFrame(index=[col for col in load_profiles.columns if col != 'Datetime'],
                           data=imports, columns=['Annual_kWh'])
    price_data['date_time_no_year'] = price_data['SETTLEMENTDATE'].dt.month.astype(str) + '_' \
                                      + price_data['SETTLEMENTDATE'].dt.day.astype(str) + '_' \
                                      + price_data['SETTLEMENTDATE'].dt.time.astype(str)
    price_data = price_data.drop('SETTLEMENTDATE', axis=1)

    load_profiles['date_time_no_year'] = load_profiles.index.month.astype(str) + '_' \
                                         + load_profiles.index.day.astype(str) + '_' \
                                         + load_profiles.index.time.astype(str)

    price_and_load = pd.merge(load_profiles, price_data, how='left', on='date_time_no_year')
    results['Bill'] = [np.nansum(price_and_load[col] * (price_and_load['RRP'].astype(float)/1000))
                       for col in load_profiles.columns if col != 'date_time_no_year']
    return results
