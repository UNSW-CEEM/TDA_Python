import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog


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
    actual_names = list(demo_file.columns[1:])
    display_names = list(demo_file.columns[1:])
    options = {}
    display_names_dict = {}
    for name, display_name in zip(actual_names, display_names):
        options[name] = ['All'] + list([str(val) for val in demo_file[name].unique()])
        display_names_dict[name] = display_name
    return {'actual_names': actual_names, "display_names": display_names_dict, "options": options}


def filter_load_data(raw_data, filtered_demo_info):
    customer_id = [c_id for c_id in list(filtered_demo_info['CUSTOMER_KEY']) if c_id in raw_data.columns]
    filtered_data = raw_data.loc[:, ['Datetime'] + customer_id]
    return filtered_data


def add_missing_customer_keys_to_demo_file_with_nan_values(raw_data, demo_info):
    customer_keys = [key for key in raw_data.columns if key != 'Datetime']
    df_with_just_customer_keys_from_load_profiles = pd.DataFrame.from_dict({'CUSTOMER_KEY': customer_keys})
    demo_info = pd.merge(demo_info, df_with_just_customer_keys_from_load_profiles, how='outer', on='CUSTOMER_KEY')
    return demo_info


def filter_demo_info(demo_info, filter_options):
    filtered = False
    for column_name, selected_options in filter_options.items():
        if 'All' not in selected_options:
            demo_info = demo_info[demo_info[column_name].isin([selected_options])]
            filtered = True
    return demo_info, filtered


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
        results_to_plot[name] = {}
        if name in retail_results_by_case.keys():                
            results_to_plot[name]['Retailer'] = retail_results_by_case[name]
        if name in network_results_by_case.keys():
            results_to_plot[name]['Network'] = network_results_by_case[name]
        if name in wholesale_results_by_case.keys():
            results_to_plot[name]['Wholesale'] = wholesale_results_by_case[name]
    return results_to_plot


def get_file_to_load_from_user(file_type, file_extension):
    root = tk.Tk()
    root.geometry('0x0+0+0')
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.overrideredirect(True)
    file_path = filedialog.askopenfilename(parent=root, filetypes=((file_type, file_extension),))
    return file_path


def get_save_name_from_user(type_name, extension):
    root = tk.Tk()
    root.geometry('0x0+0+0')
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.overrideredirect(True)
    file_path = filedialog.asksaveasfilename(parent=root, filetypes=((type_name, extension),))
    return file_path


def get_project_name_from_file_path(file_path):
    return file_path.split('/')[-1][:-4]


def add_file_extension_if_needed(file_path, extension):
    if file_path[-4:] != extension:
        file_path = file_path + extension
    return file_path
