import os
import pandas as pd


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
    return load_data



