import pandas as pd
from datetime import timedelta
import numpy as np


def calc_mean_daily_load(load):
    load['READING_DATETIME'] = pd.to_datetime(load['READING_DATETIME'])
    load['READING_DATETIME'] = load['READING_DATETIME'] - timedelta(seconds=1)
    load['READING_DATETIME'] = load['READING_DATETIME'].astype(str)
    load = load.groupby([load['READING_DATETIME'].str[:10]]).sum()
    load.index.name = 'READING_DATETIME'
    load = load.reset_index()
    load['mean'] = [np.nanmean(row[1:], dtype=float) for row in load.values]
    load = load.loc[:, ("READING_DATETIME", 'mean')]
    return load


def find_loads_demographic_file(load_file_name):
    load_2_demo_map = pd.read_csv('data/load_2_demo_map.csv')
    if load_file_name in list(load_2_demo_map['load']):
        demographic_file_name = load_2_demo_map[load_2_demo_map['load'] == load_file_name]['demo'].iloc[0]
    else:
        demographic_file_name = ''
    return demographic_file_name


def find_loads_demographic_config_file(load_file_name):
    load_2_demo_map = pd.read_csv('data/load_2_demo_map.csv')
    if load_file_name in list(load_2_demo_map['load']):
        demo_config_file_name = load_2_demo_map[load_2_demo_map['load'] == load_file_name]['demo_config'].iloc[0]
    else:
        demo_config_file_name = ''
    return demo_config_file_name


def format_tariff_data_for_display(raw_tariff_json):
    display_format = {
                      'name': "example",
                      'type': "great_tariff",
                      'state': "nsw",
                      'sub_components': {
                          'DUOS':
                              { 'table_data':
                                    {'table_header': ['', 'Months', 'TimeIntervals', 'Unit', 'Value', 'Weekday', 'Weekend'],
                                     'table_rows': [['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                    ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                    ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                    ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                    ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                    ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                    ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True']]},
                                'daily_charge': '1.0',
                                'energy_charge': '2.0'},
                          'NUOS':
                              {'table_data':
                                    {'table_header': ['', 'Months', 'TimeIntervals', 'Unit', 'Value', 'Weekday', 'Weekend'],
                                    'table_rows': [['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                  ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                  ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                  ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                  ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                  ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True'],
                                                  ['1', '1,2,3', '["00:00","07:00"]', '$/kWh', '0.3', 'True', 'True']]},
                                'daily_charge': '1.0',
                                'energy_charge': '2.0'}
                      }
    }
    return display_format