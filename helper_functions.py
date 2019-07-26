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
    display_format['Parameters'] = {}
    if raw_tariff_json['ProviderType'] == 'Network':
        for parameter_name, parameter in raw_tariff_json['Parameters'].items():
            table_set = add_tables(parameter)
            display_format['Parameters'][parameter_name] = table_set
    else:
        table_set = add_tables(raw_tariff_json['Parameters'])
        display_format['Parameters']["Retail"] = table_set
    return display_format


def add_tables(parameter):
    table_set = {}
    for component_name, component in parameter.items():
        table_data = {'table_rows': []}
        if contains_sub_dict(component):
            table_data['table_header'] = ['Name']
            for sub_component, sub_details in component.items():
                row = [sub_component]
                table_data = add_row(sub_details, row, table_data)
        else:
            table_data['table_header'] = []
            row = []
            table_data = add_row(component, row, table_data)
        table_set[component_name] = table_data
    return table_set


def add_row(component, initial_row, table_data):
    for column_name, column_value in component.items():
        if column_name not in table_data['table_header']:
            table_data['table_header'].append(str(column_name))
        initial_row.append(str(column_value))
    table_data['table_rows'].append(initial_row)
    return table_data


def contains_two_levels_of_dict(test_dict):
    has_sub_dict = False
    for key, value in test_dict.items():
        if contains_sub_dict(value):
            has_sub_dict = True
    return has_sub_dict


def contains_sub_dict(test_dict):
    is_dict = False
    for key, value in test_dict.items():
        if type(value) is dict:
            is_dict = True
    return is_dict


def format_tariff_data_for_storage(display_formatted_tariff):
    storage_format = copy.deepcopy(display_formatted_tariff)

    storage_format['Parameters'] = {}
    if display_formatted_tariff['ProviderType'] == 'Network':
        for parameter_name, parameter in display_formatted_tariff['Parameters'].items():
            table_set = add_dicts(parameter)
            storage_format['Parameters'][parameter_name] = table_set
    else:
        table_set = add_dicts(display_formatted_tariff['Parameters']["Retail"])
        storage_format['Parameters'] = table_set
    return storage_format


def add_dicts(parameter):
    dict_set = {}
    for component_name, component in parameter.items():
        if 'Name' in component['table_header']:
            sub_dict = {}
            for row in component['table_rows']:
                sub_dict[row[0]] = dict(zip(component['table_header'][1:], row[1:]))
            dict_set[component_name] = sub_dict
        else:
            dict_set[component_name] = dict(zip(component['table_header'], component['table_rows'][0]))
    return dict_set


def strip_tariff_to_single_component(tariff, component_name):
    components_to_delete = []
    for parameter_name, parameter in tariff['Parameters'].items():
        if parameter_name != component_name:
            components_to_delete.append(parameter_name)
    for component in components_to_delete:
        tariff['Parameters'].pop(component)
    return tariff
