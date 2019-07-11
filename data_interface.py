import os
import pandas as pd
import feather
import helper_functions
import json


def extract_load_options(folder_path):
    load_options = [file[:-4] for file in os.listdir(folder_path) if file[0:4] == 'load']
    return load_options


def get_demographics_table(folder_path, load_file, mapping_file):
    mapping_table = pd.read_csv(folder_path + '/' + mapping_file)
    demographics_filename = mapping_table[mapping_table['Load File'] == load_file]['Demographic File'][0]
    demographics_table = pd.read_csv(folder_path + '/' + demographics_filename + '.csv', dtype=str)
    return demographics_table


def extract_demographics_options(demographic_table):
    options = {}
    for column in demographic_table.columns:
        options[column] = list(demographic_table[column].unique())
    return options


def get_load_table(folder_path, load_file):
    load_data = pd.read_csv(folder_path + load_file)
    load_data['READING_DATETIME'] = pd.to_datetime(load_data['READING_DATETIME'])
    load_data = pd.melt(load_data, id_vars=['READING_DATETIME'],
                        value_vars=[x for x in load_data.columns if x != 'READING_DATETIME'],
                        var_name='CUSTOMER_KEY', value_name='Energy_kWh')
    x=1
    return load_data


def get_load_table_alt(folder_path, load_file):
    load_data = feather.read_dataframe(folder_path + load_file)
    return load_data


def filter_load_data(raw_data, file_name, filter_options):
    # Create filtered set of customer keys.
    demo_info_file_name = helper_functions.find_loads_demographic_file(file_name)
    demo_info = pd.read_csv('data/' + demo_info_file_name, dtype=str)

    filtered = False

    for column_name, selected_options in filter_options.items():
        if 'All' not in selected_options:
            demo_info = demo_info[demo_info[column_name].isin([selected_options])]
            filtered = True

    filtered_data = raw_data[raw_data['CUSTOMER_KEY'].isin(demo_info['CUSTOMER_KEY'])]

    return filtered, filtered_data


def n_users(load_data):
    n = len(set(load_data['CUSTOMER_KEY']))
    return n


def get_tariff(requested_tariff):
    with open('data/NetworkTariffs.json') as json_file:
        network_tariffs = json.load(json_file)

    # Look at each tariff and find the first one that matches the requested name.
    for tariff in network_tariffs:
        if tariff['Name'] == requested_tariff:
            selected_tariff = tariff

    return selected_tariff

