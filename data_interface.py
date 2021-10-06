import pandas as pd
import feather
import json


def get_load_table(folder_path, load_file):
    # @todo: if cannot find load file throw an error

    load_data = feather.read_dataframe(folder_path + load_file + '.feather')

    load_data[load_data.columns[0]] = pd.to_datetime(load_data[load_data.columns[0]])
    load_data.rename(columns={load_data.columns[0]: 'Datetime'}, inplace=True)
    load_data = load_data.sort_values(by=['Datetime'])
    load_data = load_data.set_index('Datetime')
    return load_data


def get_tariff(tariff_type, requested_tariff):
    # print("tariff_type in get_tariff ------------", type(tariff_type), tariff_type)
    # print("requested_tariff in get_tariff ------------", type(requested_tariff), requested_tariff)
    tariffs = get_tariffs(tariff_type)
    # Look at each tariff and find the first one that matches the requested name.
    for tariff in tariffs:
        if tariff['Name'] == requested_tariff:
            selected_tariff = tariff
    return selected_tariff


def get_tariffs(tariff_type):
    if tariff_type == 'network_tariff_selection_panel':
        with open('data/NetworkTariffs.json') as json_file:
            tariffs = json.load(json_file)[0]['Tariffs']
        with open('data/UserDefinedNetworkTariffs.json') as json_file:
            user_tariffs = json.load(json_file)
    else:
        with open('data/RetailTariffs.json') as json_file:
            tariffs = json.load(json_file)[0]['Tariffs']
        with open('data/UserDefinedRetailTariffs.json') as json_file:
            user_tariffs = json.load(json_file)
    tariffs = tariffs + user_tariffs
    return tariffs


def find_loads_demographic_file(load_file_name):
    load_2_demo_map = pd.read_csv('data/load_2_demo_map.csv')

    # @todo: if cannot find demographic file throw an error
    if load_file_name in list(load_2_demo_map['load']):
        demographic_file_name = load_2_demo_map[load_2_demo_map['load'] == load_file_name]['demo'].iloc[0]
    else:
        return False
    return demographic_file_name




