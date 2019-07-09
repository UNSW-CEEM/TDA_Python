import pandas as pd
from datetime import timedelta
import numpy as np
import copy
import math

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
    display_format = copy.deepcopy(raw_tariff_json)

    for parameter_name, parameter in raw_tariff_json['Parameters'].items():
        for component_name, component in parameter.items():
            table_data = {}
            table_data['table_header'] = ['Name']
            table_data['table_rows'] = []
            if ((component_name == 'Energy' and 'Unit' not in component.keys()) or
                (component_name != 'Daily' and component_name != 'Energy')):
                for sub_component, sub_details in component.items():
                    row = [sub_component]
                    for column_name, column_value in sub_details.items():
                        if column_name not in table_data['table_header']:
                            table_data['table_header'].append(str(column_name))
                        row.append(str(column_value))
                    table_data['table_rows'].append(row)
                display_format['Parameters'][parameter_name]['table_data'] = table_data
                del display_format['Parameters'][parameter_name][component_name]

    return display_format


def format_tariff_data_for_storage(display_formatted_tariff):
    storage_format = copy.deepcopy(display_formatted_tariff)

    for parameter_name, parameter in display_formatted_tariff['Parameters'].items():
        for component_name, component in parameter.items():
            charges = {}
            if component_name == 'table_data':
                for row in component['table_rows']:
                    for counter, item in enumerate(row):
                        if counter == 0:
                            charges[item] = {}
                        else:
                            if component['table_header'][counter] in ['Unit']:
                                charges[row[0]][component['table_header'][counter]] = item
                            else:
                                if item == 'inf':
                                    charges[row[0]][component['table_header'][counter]] = math.inf
                                else:
                                    charges[row[0]][component['table_header'][counter]] = eval(item)
                del storage_format['Parameters'][parameter_name][component_name]
                storage_format['Parameters'][parameter_name]['Energy'] = charges

    return storage_format

