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
    load_data = feather.read_dataframe(folder_path + load_file)
    load_data['Datetime'] = pd.to_datetime(load_data['READING_DATETIME'])
    load_data = load_data.sort_values(by=['Datetime'])
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

    customer_id = [c_id for c_id in list(demo_info['CUSTOMER_KEY']) if c_id in raw_data.columns]

    filtered_data = raw_data.loc[:, ['Datetime'] + customer_id]

    return filtered, filtered_data


def n_users(load_data):
    n = len(load_data.columns) - 1
    return n


def get_tariff(tariff_panel, requested_tariff):
    tariffs = get_tariffs(tariff_panel)
    # Look at each tariff and find the first one that matches the requested name.
    for tariff in tariffs:
        if tariff['Name'] == requested_tariff:
            selected_tariff = tariff

    return selected_tariff


def get_tariffs(tariff_panel):
    if tariff_panel == 'network_tariff_selection_panel':
        with open('data/NetworkTariffs.json') as json_file:
            tariffs = json.load(json_file)
        with open('data/UserDefinedNetworkTariffs.json') as json_file:
            user_tariffs = json.load(json_file)
    else:
        with open('data/RetailTariffs.json') as json_file:
            tariffs = json.load(json_file)
        with open('data/UserDefinedRetailTariffs.json') as json_file:
            user_tariffs = json.load(json_file)
    tariffs = tariffs + user_tariffs
    return tariffs




