import pandas as pd
import numpy as np

def get_unique_default_case_name(names_in_use):
    base_name = "Case "
    not_unique = True
    number = 1
    while not_unique:
        test_name = base_name + str(number)
        if test_name not in names_in_use:
            break
        number += 1
    return test_name


def get_demographic_options_from_demo_file(demo_file):
    n = len(demo_file.columns) if len(demo_file.columns) < 11 else 11
    actual_names = list(demo_file.columns[1:n])
    display_names = list(demo_file.columns[1:n])
    options = {}
    display_names_dict = {}
    for name, display_name in zip(actual_names, display_names):
        options[name] = ['All'] + list([str(val) for val in demo_file[name].unique()])
        display_names_dict[name] = display_name
    return {'actual_names': actual_names, "display_names": display_names_dict, "options": options}


def filter_load_data(raw_data, demo_info, filter_options):
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


def get_tariff_by_case(case_name, tariff_type, network_tariffs_by_case, retail_tariffs_by_case):
    tariff = 'None'
    if tariff_type == 'network_tariff_selection_panel':
        if case_name in network_tariffs_by_case.keys():
            tariff = network_tariffs_by_case[case_name]
    else:
        if case_name in retail_tariffs_by_case.keys():
            tariff = retail_tariffs_by_case[case_name]
    return tariff


def get_results_subset_to_plot(case_names, retail_results_by_case, network_results_by_case,
                               wholesale_results_by_case):
    results_to_plot = {}
    for name in case_names:
        if name in retail_results_by_case.keys():
            results_to_plot[name] = retail_results_by_case[name]
        elif name in network_results_by_case.keys():
            results_to_plot[name] = network_results_by_case[name]
        elif name in wholesale_results_by_case.keys():
            results_to_plot[name] = wholesale_results_by_case[name]
    return results_to_plot


def calc_wholesale_energy_costs(price_data, load_profiles):
    imports = [np.nansum(load_profiles[col].values[load_profiles[col].values > 0])
               for col in load_profiles.columns if col != 'Datetime']
    results = pd.DataFrame(index=[col for col in load_profiles.columns if col != 'Datetime'],
                           data=imports, columns=['Annual_kWh'])
    price_data['date_time_no_year'] = price_data['SETTLEMENTDATE'].dt.month.astype(str) + '_' \
                                      + price_data['SETTLEMENTDATE'].dt.day.astype(str) + '_' \
                                      + price_data['SETTLEMENTDATE'].dt.time.astype(str)
    price_data = price_data.drop('SETTLEMENTDATE', axis=1)
    load_profiles['date_time_no_year'] = load_profiles['Datetime'].dt.month.astype(str) + '_' \
                                         + load_profiles['Datetime'].dt.day.astype(str) + '_' \
                                         + load_profiles['Datetime'].dt.time.astype(str)
    load_profiles = load_profiles.drop('Datetime', axis=1)
    price_and_load = pd.merge(load_profiles, price_data, how='left', on='date_time_no_year')
    results['Bill'] = [np.nansum(price_and_load[col] * (price_and_load['RRP'].astype(float)/1000))
                       for col in load_profiles.columns if col != 'date_time_no_year']
    return results