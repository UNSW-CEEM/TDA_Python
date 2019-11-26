from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import subprocess
import platform
import sys
import pandas as pd
import helper_functions
import plotly
import json
from make_load_charts import chart_methods
from make_results_charts import singe_variable_chart, dual_variable_chart, single_case_chart
from import_delete_data import check_valid_filetype, check_file_exists, check_load_2_demo_map, \
                               check_data_is_not_default, add_to_load_2_demo_map, \
                               load_data_to_dataframe, generic_data_to_dataframe
import data_interface
import Bill_Calc
import format_case_for_export
import format_chart_data_for_export
import start_up_procedures
from tariff_processing import format_tariff_data_for_display, format_tariff_data_for_storage, \
                              get_options_from_tariff_set, _make_dict
from make_price_charts import get_price_chart
from wholesale_energy import get_wholesale_prices, calc_wholesale_energy_costs
import pickle
from session_data import InMemoryData
from openpyxl import Workbook
import errors
import logging
import validate_component_table_cell_values
import check_time_of_use_coverage
import end_user_tech
import math
import feather
import csv
import webbrowser

enable_logging = False

# Initialise object for holding the current session/project's data.
current_session = InMemoryData()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if getattr(sys, 'frozen', False):
    template_folder = resource_path('templates')
    static_folder = resource_path('static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)


# Here you go to http://127.0.0.1:5000/
@app.route('/')
def index():
    return render_template('index.html')


# Start logging
if enable_logging:
    logging.basicConfig(filename='tda_log_file.txt', filemode='w', level=logging.DEBUG)
    logger = logging.getLogger(__name__)
else:
    logger = None


@app.route('/tariff_selectors')
def tariff_selectors():
    return render_template('tariff_selectors.html')


@app.route('/tariff_table')
def tariff_table():
    return render_template('tariff_table.html')


@app.route('/load_names')
@errors.parse_to_user_and_log(logger)
def load_names():
    # Get the list of load files for the user to choose from.
    names = []
    for file_name in os.listdir('data/load/'):
        names.append(file_name.split('.')[0])

    data = {
        "names": names,
        "current_load": current_session.raw_data_name
    }
    return jsonify(data)


@app.route('/solar_names')
@errors.parse_to_user_and_log(logger)
def solar_names():
    # Get the list of load files for the user to choose from.
    names = []
    for file_name in os.listdir('data/solar_profiles/'):
        names.append(file_name.split('.')[0])

    return jsonify(names)


@app.route('/network_load_names')
@errors.parse_to_user_and_log(logger)
def network_load_names():
    # Get the list of load files for the user to choose from.
    names = []
    for file_name in os.listdir('data/network_loads/'):
        names.append(file_name.split('.')[0])
    return jsonify(names)


@app.route('/get_tariff_set_options/<tariff_type>')
@errors.parse_to_user_and_log(logger)
def get_tariff_set_options(tariff_type):
    # Get the versions of the tariff data base for the user to choose from.
    tariff_set_options = []
    # Determines if 'Network' or 'Retail' results are returned
    folder = 'data/{}_tariff_set_versions/'.format(tariff_type)
    for file_name in os.listdir(folder):
        tariff_set_options.append(file_name.split('.')[0])
    return jsonify(tariff_set_options)


@app.route('/set_tariff_set_in_use', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def set_tariff_set_in_use():
    # Replace the network or retail data sets in the main 'data' folder with a set from the 'tariff_set_versions' folder
    # Allows the user to continue using older versions of the tariff data base.
    request_details = request.get_json()

    # Determine if 'Retail' of 'Network tariffs are being updated and sets the correct version to retrieve.
    folder_and_name = 'data/{}_tariff_set_versions/{}.json'.format(request_details['type'], request_details['version'])

    # Open the tariff file that is going to be used.
    with open(folder_and_name, 'rt') as json_file:
        tariffs = json.load(json_file)

    # Write contents to the file in the 'data' folder that acts as the active tariff data set.
    with open('data/{}Tariffs.json'.format(request_details['type']), 'wt') as json_file:
        json.dump(tariffs, json_file)
    return jsonify({'message': 'done'})


@app.route('/put_load_profiles_in_memory', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def put_load_profiles_in_memory():
    load_request = request.get_json()
    file_name = load_request['file_name']
    if file_name != 'Select one':
        current_session.raw_data_name = file_name
        # Get raw load data.
        if file_name not in current_session.raw_data:
            current_session.raw_data[file_name] = data_interface.get_load_table('data/load/', load_request['file_name'])
    else:
        current_session.raw_data_name = ''
    return jsonify({'message': 'done'})


@app.route('/filtered_load_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def filtered_load_data():
    load_request = request.get_json()
    file_name = load_request['file_name']

    ######################################
    # Filtering Data

    # Should only filter once for every new load data selected
    if current_session.filter_state != load_request:
        current_session.filter_state = load_request
        raw_data = current_session.raw_data[file_name]

        # Filter by missing data
        missing_data_limit = load_request['missing_data_limit']
        current_session.filter_missing_data = raw_data[raw_data.columns[raw_data.isnull().mean() <= missing_data_limit]]

        # Down sample data randomly
        number_of_loads = len(current_session.filter_missing_data.columns)
        number_of_loads_downsampled = math.ceil(number_of_loads * load_request['sample_fraction'])
        if number_of_loads_downsampled < 1:
            number_of_loads_downsampled = 1
        current_session.downsample_data = current_session.filter_missing_data.sample(n=number_of_loads_downsampled, axis=1)

        # Filter data by demographic
        demo_info_file_name = data_interface.find_loads_demographic_file(file_name)
        demo_info = feather.read_dataframe('data/demographics/' + demo_info_file_name + '.feather').astype(str)
        demo_info = helper_functions.add_missing_customer_keys_to_demo_file_with_nan_values(
            current_session.downsample_data, demo_info)

        current_session.filtered_demo_info, current_session.is_filtered = \
            helper_functions.filter_demo_info(demo_info, load_request['filter_options'])
        current_session.filtered_data = helper_functions.filter_load_data(
            current_session.downsample_data, current_session.filtered_demo_info)
    else:
        pass

    ######################################
    # Create network load profile:
    current_session.network_load = network_load(load_request)

    ######################################
    # Creating Charts
    chart_type = load_request['chart_type']

    # Create the requested chart data if it does not already exist.
    if file_name not in current_session.raw_charts:
        current_session.raw_charts[file_name] = {}

    # prepare chart data and n_users

    current_session.filtered_charts = {file_name: {}}

    if chart_type not in current_session.raw_charts[file_name]:
        if chart_type in ['Annual Average Profile', 'Daily kWh Histogram']:
            current_session.raw_charts[file_name][chart_type] = \
                chart_methods[chart_type](current_session.downsample_data,
                                          current_session.filtered_data, series_name=['All'])
        else:
            current_session.raw_charts[file_name][chart_type] = \
                chart_methods[chart_type](current_session.filtered_data)

    if current_session.is_filtered:
        if chart_type in ['Annual Average Profile', 'Daily kWh Histogram']:
            current_session.filtered_charts[file_name][chart_type] = \
                chart_methods[chart_type](current_session.downsample_data, current_session.filtered_data,
                                          series_name=['All', 'Selected'])
        else:
            current_session.filtered_charts[file_name][chart_type] = \
                chart_methods[chart_type](current_session.filtered_data)

        chart_data = current_session.filtered_charts[file_name][chart_type]
        n_users = helper_functions.n_users(current_session.filtered_data)
    else:
        chart_data = current_session.raw_charts[file_name][chart_type]
        n_users = helper_functions.n_users(current_session.downsample_data)

    # Format as json.
    return_data = {"n_users": n_users, "chart_data": chart_data}
    return_data = json.dumps(return_data, cls=plotly.utils.PlotlyJSONEncoder)
    return return_data


@errors.parse_to_user_and_log(logger)
def network_load(load_request):
    filter_option = load_request['network_load'].strip()

    if filter_option == 'full':
        agg_network_load = pd.DataFrame(current_session.filter_missing_data.sum(axis=1), columns=['load'])

    elif filter_option == 'filtered':
        agg_network_load = pd.DataFrame(current_session.filtered_data.sum(axis=1), columns=['load'])

    else:
        file_name = filter_option
        synthetic_load = feather.read_dataframe('data/network_loads/' + file_name + '.feather')
        synthetic_load.rename(columns={synthetic_load.columns[0]: 'Datetime'}, inplace=True)
        synthetic_load = synthetic_load.set_index('Datetime')
        agg_network_load = pd.DataFrame(synthetic_load.sum(axis=1), columns=['load'])

    return agg_network_load


@app.route('/net_load_chart_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def net_load_chart_data():
    # TODO: Update this function to produce the actual plots of net load we want.
    load_request = request.get_json()
    chart_type = load_request['chart_type']
    if chart_type in ['Annual Average Profile', 'Daily kWh Histogram']:
        chart_data = chart_methods[chart_type](current_session.downsample_data,
                                               current_session.end_user_tech_data['final_net_profiles'],
                                               series_name=['All', 'Selected'])
    elif chart_type == 'Annual Average Energy Flow Profile':
        chart_data = chart_methods[chart_type](current_session.end_user_tech_data)
    else:
        chart_data = chart_methods[chart_type](current_session.end_user_tech_data['final_net_profiles'])

    # Format as json.
    return_data = {"chart_data": chart_data}
    return_data = json.dumps(return_data, cls=plotly.utils.PlotlyJSONEncoder)
    return return_data


@app.route('/get_case_default_name', methods=['GET'])
@errors.parse_to_user_and_log(logger)
def get_case_default_name():
    # Default case names are of the format 'Case n'. If 'Case 1' is in use then try 'Case 2' etc until a case default
    # case name that is not in use is found.
    name = helper_functions.get_unique_default_case_name(current_session.project_data.load_file_name_by_case.keys())
    return jsonify({'name': name})


@app.route('/add_case', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def add_case():
    # Using the currently active tariff (network tariff by default at the moment) calculate the bill for all load
    # profiles and save the results. Also save the other details associated with the case.

    # Unpack request details
    case_details = request.get_json()
    case_name = case_details['case_name']
    load_file_name = current_session.raw_data_name
    filter_options = current_session.filter_state
    retail_tariff_name = case_details['retail_tariff_name']
    network_tariff_name = case_details['network_tariff_name']
    wholesale_year = case_details['wholesale_price_details']['year']
    wholesale_state = case_details['wholesale_price_details']['state']

    if current_session.end_user_tech_sample_applied == False:
        current_session.end_user_tech_data['final_net_profiles'] = current_session.filtered_data
    else:
        current_session.project_data.end_user_tech_details_by_case[case_name] = current_session.end_user_tech_details

    # Save demographic info for case
    current_session.project_data.demographic_info_by_case[case_name] = current_session.filtered_demo_info

    if network_tariff_name != 'None':
        network_tariff = data_interface.get_tariff('network_tariff_selection_panel', network_tariff_name)
        network_results = Bill_Calc.bill_calculator(current_session.end_user_tech_data['final_net_profiles'],
                                                    network_tariff)
        network_results['LoadInfo'].index.name = 'CUSTOMER_KEY'
        network_results['LoadInfo'] = network_results['LoadInfo'].reset_index()

        current_session.project_data.network_results_by_case[case_name] = network_results
        current_session.project_data.network_tariffs_by_case[case_name] = network_tariff

    if retail_tariff_name != 'None':
        retail_tariff = data_interface.get_tariff('retail_tariff_selection_panel', retail_tariff_name)
        retail_results = Bill_Calc.bill_calculator(current_session.end_user_tech_data['final_net_profiles'], retail_tariff)
        retail_results['LoadInfo'].index.name = 'CUSTOMER_KEY'
        retail_results['LoadInfo'] = retail_results['LoadInfo'].reset_index()
        current_session.project_data.retail_results_by_case[case_name] = retail_results
        current_session.project_data.retail_tariffs_by_case[case_name] = retail_tariff

    if (wholesale_year != 'None') & (wholesale_state != 'None'):
        price_data = get_wholesale_prices(wholesale_year, wholesale_state)
        wholesale_results = calc_wholesale_energy_costs(price_data,  current_session.end_user_tech_data['final_net_profiles'].copy())
        wholesale_results.index.name = 'CUSTOMER_KEY'
        wholesale_results = wholesale_results.reset_index()
        current_session.project_data.wholesale_results_by_case[case_name] = wholesale_results
        current_session.project_data.wholesale_price_info_by_case[case_name] = {}
        current_session.project_data.wholesale_price_info_by_case[case_name]['year'] = wholesale_year
        current_session.project_data.wholesale_price_info_by_case[case_name]['state'] = wholesale_state

    # Save input data and settings associated with the case.
    current_session.load_by_case[case_name] = current_session.end_user_tech_data['final_net_profiles']
    current_session.project_data.load_file_name_by_case[case_name] = load_file_name
    current_session.project_data.load_n_users_by_case[case_name] = \
        helper_functions.n_users(current_session.end_user_tech_data['final_net_profiles'])
    current_session.project_data.filter_options_by_case[case_name] = filter_options
    return jsonify({'message': 'done'})


@app.route('/get_case_tariff', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_case_tariff():
    # Get the tariff associated with a particular case.
    request_details = request.get_json()
    case_name = request_details['case_name']
    tariff_type = request_details['tariff_type']
    tariff = helper_functions.get_tariff_by_case(case_name, tariff_type,
                                                 current_session.project_data.network_tariffs_by_case,
                                                 current_session.project_data.retail_tariffs_by_case)
    if tariff != 'None':
        tariff = format_tariff_data_for_display(tariff)
    return jsonify(tariff)


@app.route('/get_case_load', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_case_load():
    # Get the set of load profiles associated with a particular case.
    case_name = request.get_json()
    return jsonify({'n_users': current_session.project_data.load_n_users_by_case[case_name],
                    'database': current_session.project_data.load_file_name_by_case[case_name]})


@app.route('/get_case_demo_options', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_case_demo_options():
    # Get the demographic filtering options associated with a particular case.
    case_name = request.get_json()
    return jsonify(current_session.project_data.filter_options_by_case[case_name])


@app.route('/get_case_tech_options', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_case_tech_options():
    # Get the demographic filtering options associated with a particular case.
    case_name = request.get_json()
    return jsonify(current_session.project_data.end_user_tech_details_by_case[case_name]['tech_details'])


@app.route('/delete_case', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def delete_case():
    # Delete all data associated with a particular case.
    case_name = request.get_json()
    if case_name in current_session.load_by_case.keys():
        current_session.load_by_case.pop(case_name)
    if case_name in current_session.project_data.network_results_by_case.keys():
        current_session.project_data.network_results_by_case.pop(case_name)
    if case_name in current_session.project_data.retail_results_by_case.keys():
        current_session.project_data.retail_results_by_case.pop(case_name)
    if case_name in current_session.project_data.retail_tariffs_by_case.keys():
        current_session.project_data.retail_tariffs_by_case.pop(case_name)
    if case_name in current_session.project_data.network_tariffs_by_case.keys():
        current_session.project_data.network_tariffs_by_case.pop(case_name)
    if case_name in current_session.project_data.load_file_name_by_case.keys():
        current_session.project_data.load_file_name_by_case.pop(case_name)
    if case_name in current_session.project_data.load_n_users_by_case.keys():
        current_session.project_data.load_n_users_by_case.pop(case_name)
    if case_name in current_session.project_data.end_user_tech_details_by_case.keys():
        current_session.project_data.end_user_tech_details_by_case.pop(case_name)
    return jsonify({'message': 'done'})


@app.route('/get_single_variable_chart', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_single_variable_chart():
    details = request.get_json()
    chart_name = details['chart_name']
    case_names = details['case_names']

    results_to_plot = helper_functions.get_results_subset_to_plot(case_names, 
                                                                  current_session.project_data.retail_results_by_case,
                                                                  current_session.project_data.network_results_by_case,
                                                                  current_session.project_data.wholesale_results_by_case)

    load_and_results_to_plot = {'results': results_to_plot, 'load': current_session.load_by_case}
    return singe_variable_chart(chart_name, load_and_results_to_plot)


@app.route('/get_dual_variable_chart', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_dual_variable_chart():
    details = request.get_json()
    case_names = details['case_names']
    results_to_plot = helper_functions.get_results_subset_to_plot(case_names, 
                                                                  current_session.project_data.retail_results_by_case,
                                                                  current_session.project_data.network_results_by_case,
                                                                  current_session.project_data.wholesale_results_by_case)

    load_and_results_to_plot = {'results': results_to_plot, 'load': current_session.load_by_case,
                                'network_load': current_session.network_load}

    return dual_variable_chart(load_and_results_to_plot, details)


@app.route('/get_single_case_chart', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_single_case_chart():
    details = request.get_json()
    chart_name = details['chart_name']
    case_name = details['case_name']
    results_to_plot = helper_functions.get_results_subset_to_plot(
        [case_name],
        current_session.project_data.retail_results_by_case,
        current_session.project_data.network_results_by_case,
        current_session.project_data.wholesale_results_by_case)

    if case_name not in results_to_plot.keys():
        results_to_plot = None
    else:
        results_to_plot = results_to_plot[case_name]

    single_case_results_to_plot = {'results': results_to_plot}

    return single_case_chart(chart_name, single_case_results_to_plot)


@app.route('/get_demo_options/<name>')
@errors.parse_to_user_and_log(logger)
def get_demo_options(name):
    demo_file_name = data_interface.find_loads_demographic_file(name) + '.feather'

    if demo_file_name != '' and demo_file_name in os.listdir('data/demographics/'):
        demo = feather.read_dataframe('data/demographics/' + demo_file_name).astype(str)
        demo = helper_functions.add_missing_customer_keys_to_demo_file_with_nan_values(
            current_session.raw_data[current_session.raw_data_name], demo)
        demo_options = helper_functions.get_demographic_options_from_demo_file(demo)
    else:
        demo_options = {'actual_names': [], "display_names": {}, "options": {}}

    return jsonify(demo_options)


@app.route('/wholesale_price_options', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def wholesale_price_options():
    # First year to access data from.
    year = 2012
    # Month to check for data.
    month = 12
    # url to check for data at.
    aemo_name = 'data/aemo_raw_cache/PUBLIC_DVD_TRADINGPRICE_{}{}010000.csv'
    # Status to keep checking for new data on.
    last_year = 'complete'
    # Add years to the list that the user can select from where that year has an AMEO
    years = []
    while last_year == 'complete':
        name_to_check = aemo_name.format(year, month)
        if os.path.isfile(name_to_check):
            years.append(year)
            year += 1
        else:
            last_year = 'not complete'
    # Hard coded regions that the user can select from.
    states = ['NSW', "VIC", 'TAS', 'QLD', 'SA']
    return jsonify({'states': states, 'years': years})


@app.route('/wholesale_prices', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def wholesale_price_chart_data():
    request_details = request.json
    if (request_details['year'] != 'None') & (request_details['state'] != 'None'):
        price_data = get_wholesale_prices(request_details['year'], request_details['state'])
    else:
        price_data = pd.DataFrame(columns=['SETTLEMENTDATE', 'RRP'])
        price_data['SETTLEMENTDATE'] = pd.to_datetime(price_data['SETTLEMENTDATE'])
    chart_data = get_price_chart(price_data, request_details['chart_type'])
    return chart_data


@app.route('/get_wholesale_price_info', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_wholesale_price_info():
    case_name = request.json
    if case_name in current_session.project_data.wholesale_price_info_by_case.keys():
        info = {'state': current_session.project_data.wholesale_price_info_by_case[case_name]['state'],
                'year': current_session.project_data.wholesale_price_info_by_case[case_name]['year']}
    else:
        info = 'None'
    return jsonify(info)


@app.route('/create_end_user_tech_from_sample_from_gui', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def create_end_user_tech_from_sample_from_gui():
    details = request.json
    current_session.end_user_tech_sample = end_user_tech.create_sample(details, current_session.filtered_data)
    current_session.end_user_tech_data = end_user_tech.calc_net_profiles(current_session.filtered_data,
                                                                         current_session.network_load,
                                                                         current_session.end_user_tech_sample)
    current_session.end_user_tech_sample_applied = True
    current_session.end_user_tech_details = details
    return jsonify({'message': 'Done!'})


@app.route('/load_end_user_tech_from_sample_from_file', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def load_end_user_tech_from_sample_from_file():
    file = request.files['file']
    file.save('data/temp/temp.pkl')
    with open('data/temp/temp.pkl', "rb") as f:
        current_session.end_user_tech_sample = pickle.load(f)
    if current_session.end_user_tech_sample['load_details']['file_name'] + '.feather' in os.listdir('data/load/'):
        current_session.raw_data_name = current_session.end_user_tech_sample['load_details']['file_name']
        raw_data = data_interface.get_load_table('data/load/', current_session.raw_data_name)
        current_session.raw_data[current_session.raw_data_name] = raw_data
        filtered_data = raw_data.loc[:, current_session.end_user_tech_sample['customer_keys']]
        current_session.end_user_tech_data = end_user_tech.calc_net_profiles(filtered_data, current_session.network_load,
                                                                        current_session.end_user_tech_sample)
        current_session.filter_state = current_session.end_user_tech_sample['load_details']['filter_options']
        return_data = jsonify({'message': 'Done!', 'tech_inputs': current_session.end_user_tech_sample['tech_inputs']})

        current_session.end_user_tech_sample_applied = True
    else:
        return_data = jsonify({'error': 'You do not have the required load data to use this tech sample.'})
    return return_data


@app.route('/calc_sample_net_load_profiles', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def calc_sample_net_load_profiles():
    details = request.json
    current_session.end_user_tech_sample = end_user_tech.update_sample(current_session.end_user_tech_sample, details)
    current_session.end_user_tech_data = \
        end_user_tech.calc_net_profiles(current_session.filtered_data, current_session.network_load, current_session.end_user_tech_sample)

    current_session.end_user_tech_sample_applied = True
    return jsonify({'message': 'done'})


@app.route('/save_end_user_tech_sample', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def save_end_user_tech_sample():
    details = request.json
    current_session.end_user_tech_sample = end_user_tech.update_sample(current_session.end_user_tech_sample, details)
    file_path = helper_functions.get_save_name_from_user('TDA tech sample', '.tda_tech_sample')
    if file_path != '':
        file_path = helper_functions.add_file_extension_if_needed(file_path, 'tda_tech_sample')
        with open(file_path, "wb") as f:
            pickle.dump(current_session.end_user_tech_sample, f)
        message = 'saved'
    else:
        message = 'nothing saved'
    return jsonify({'message': message})


@app.route('/deactivate_tech')
@errors.parse_to_user_and_log(logger)
def deactivate_tech():
    current_session.end_user_tech_sample_applied = False
    return jsonify({'message': 'Done!'})


@app.route('/tariff_options', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def tariff_options():
    request_details = request.get_json()
    tariff_filter_state = request_details['current_options']
    tariff_panel = request_details['tariff_panel']
    # Open the tariff data set.
    tariffs = data_interface.get_tariffs(tariff_panel)
    # Given the tariff set and the current state of the filter find the remain options for the gui filters
    options = get_options_from_tariff_set(tariffs, tariff_filter_state)
    return jsonify({'tariff_options': options})


@app.route('/tariff_json', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def tariff_json():
    request_details = request.get_json()
    selected_tariff = data_interface.get_tariff(request_details['tariff_panel'],
                                                request_details['tariff_name'])
    selected_tariff = format_tariff_data_for_display(selected_tariff)
    return jsonify(selected_tariff)


@app.route('/save_tariff', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def save_tariff():
    tariff_to_save = format_tariff_data_for_storage(request.get_json())
    # Open the tariff data set.
    if tariff_to_save['ProviderType'] == 'Network':
        with open('data/UserDefinedNetworkTariffs.json', 'rt') as json_file:
            tariffs = json.load(json_file)
        tariffs.append(tariff_to_save)
        with open('data/UserDefinedNetworkTariffs.json', 'wt') as json_file:
            json.dump(tariffs, json_file)
    else:
        with open('data/UserDefinedRetailTariffs.json', 'rt') as json_file:
            tariffs = json.load(json_file)
        tariffs.append(tariff_to_save)
        with open('data/UserDefinedRetailTariffs.json', 'wt') as json_file:
            json.dump(tariffs, json_file)
    return jsonify({'message': 'done'})


@app.route('/get_active_tariff_version', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_active_tariff_version():
    details = request.get_json()
    tariff_type = details['type']
    if tariff_type == 'Network':
        with open('data/NetworkTariffs.json', 'rt') as json_file:
            tariffs = json.load(json_file)
            version = tariffs[0]['Version']
    else:
        with open('data/RetailTariffs.json', 'rt') as json_file:
            tariffs = json.load(json_file)
            version = tariffs[0]['Version']
    return jsonify({'version': version})


@app.route('/get_tou_analysis', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_tou_analysis():
    tariff_table_data = request.get_json()
    tariff_table_data = _make_dict(tariff_table_data)
    analysis_result = check_time_of_use_coverage.compile_set_of_overlapping_components_on_yearly_basis(tariff_table_data)
    return jsonify({'message': analysis_result})


@app.route('/delete_tariff', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def delete_tariff():
    request_details = request.get_json()
    # Open the tariff data set.
    if request_details['tariff_panel'] == 'network_tariff_selection_panel':
        file_name = 'NetworkTariffs'
    else:
        file_name = 'RetailTariffs'

    for file_type in ['', 'UserDefined']:
        with open('data/{}{}.json'.format(file_type, file_name), 'rt') as json_file:
            if file_type == '':
                tariffs = json.load(json_file)
                for i, tariff in enumerate(tariffs[0]['Tariffs']):
                    if request_details['tariff_name'] == tariff['Name']:
                        del tariffs[0]['Tariffs'][i]
            else:
                tariffs = json.load(json_file)
                for i, tariff in enumerate(tariffs):
                    if request_details['tariff_name'] == tariff['Name']:
                        del tariffs[i]

        with open('data/{}{}.json'.format(file_type, file_name), 'wt') as json_file:
            json.dump(tariffs, json_file)

    return jsonify({'message': 'done'})


@app.route('/import_load_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def import_load():
    file = request.files['file']
    file_name = os.path.splitext(file.filename)[0]
    file_path = 'data/temp/' + file_name
    file.save(file_path)

    # read file and load into dataframe
    load_data, demo_data = load_data_to_dataframe(file_path)

    # Check if the file format is in the correct format
    try:
        load_data[load_data.columns[0]] = pd.to_datetime(load_data[load_data.columns[0]])
        load_data.rename(columns={load_data.columns[0]: 'Datetime'}, inplace=True)
        demo_data.rename(columns={demo_data.columns[0]: 'CUSTOMER_KEY'}, inplace=True)
    except:
        return jsonify({'error': 'Invalid data format.'})

    # Add mapping of imported file into load_2_demo_map.csv
    add_to_load_2_demo_map(file_name)

    # Add import load files to database
    feather.write_dataframe(load_data, 'data/load/' + file_name + '.feather')
    feather.write_dataframe(demo_data, 'data/demographics/' + 'demo_' + file_name + '.feather')
    return jsonify({'message': "Successfully imported file."})


@app.route('/import_network_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def import_network_data():
    file = request.files['file']
    file_name = os.path.splitext(file.filename)[0]
    file_path = 'data/temp/' + file_name
    file.save(file_path)

    # read file and load into dataframe
    network_data = generic_data_to_dataframe(file_path)

    # Check if the file format is in the correct format
    try:
        network_data.rename(columns={network_data.columns[0]: 'Datetime'}, inplace=True)
    except:
        return jsonify({'error': 'Invalid data format.'})

    feather.write_dataframe(network_data, 'data/network_loads/' + file_name + '.feather')
    return jsonify({'message': "Successfully imported file."})


@app.route('/import_solar_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def import_solar_data():
    file = request.files['file']
    file_name = os.path.splitext(file.filename)[0]
    file_path = 'data/temp/' + file_name
    file.save(file_path)

    solar_data = generic_data_to_dataframe(file_path)

    # Check if the file format is in the correct format
    try:
        solar_data.rename(columns={solar_data.columns[0]: 'Datetime'}, inplace=True)
    except:
        return jsonify({'error': 'Invalid data format.'})

    feather.write_dataframe(solar_data, 'data/solar_profiles/' + file_name + '.feather')
    return jsonify({'message': "Successfully imported file."})


@app.route('/delete_solar_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def delete_solar_data():
    request_details = request.get_json()
    file_name = request_details['name']
    solar_file_path = 'data/solar_profiles/' + file_name + '.feather'

    if not check_data_is_not_default(file_name, current_session.project_data.original_solar_data):
        return jsonify({'message': "Cannot delete default data files. Can only delete data files imported by user."})

    else:
        os.remove(solar_file_path)
        return jsonify({'message': "File has been deleted."})


@app.route('/delete_load_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def delete_load_data():

    # @todo: need to remove option from selected loads (selected loads should display what is in load_2_demo_map.csv not what is in database)
    request_details = request.get_json()
    file_name = request_details['name']
    demo_file_path = 'data/demographics/' + 'demo_' + file_name + '.feather'
    load_file_path = 'data/load/' + file_name + '.feather'

    ###############################################
    # Prevent user from deleting default or original data files
    if not check_data_is_not_default(file_name, current_session.project_data.original_data):
        return jsonify({'message': "Cannot delete default data files. Can only delete data files imported by user."})

    ###############################################
    # Deleting the data files

    if check_file_exists(demo_file_path) == True & check_file_exists(load_file_path) == True:
        load_path = 'data/load/' + file_name + '.feather'
        demo_path = 'data/demographics/' + 'demo_' + file_name + '.feather'

        load_2_demo_map = pd.read_csv('data/load_2_demo_map.csv')
        new_load_2_demo_map = load_2_demo_map.copy()

        for index, files in new_load_2_demo_map.iterrows():
            if file_name.split('.')[0] == files[0]:
                new_load_2_demo_map = new_load_2_demo_map.drop(index, axis=0)
                os.remove(load_path)
                os.remove(demo_path)

        new_load_2_demo_map.to_csv('data/load_2_demo_map.csv', index=False)

        return jsonify({'message': "File has been deleted."})
    else:
        return jsonify({'message': "Cannot find file."})


@app.route('/restore_original_data_set', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def restore_original_data_set():
    files_restored = []

    with open('data/load_2_demo_map.csv', 'r') as current_file:
        files = [loaded_files.split(',', 1)[0] for loaded_files in current_file][1:]
    current_file.close()

    original_data = sorted(current_session.project_data.original_data)
    files_loaded = sorted(files)
    if files_loaded == original_data:
        return jsonify({'message': "All original files are already restored."})

    with open('data/load_2_demo_map.csv', 'w') as future_file:
        for file in files:
            if file not in current_session.project_data.original_data:
                os.remove('data/load/' + file + '.feather')
                os.remove('data/demographics/demo_' + file + '.feather')

        writer = csv.writer(future_file)
        writer.writerow(['load', 'demo'])
        for file in current_session.project_data.original_data:
            files_restored.append(file)
            writer.writerow([file, 'demo_' + file])
    future_file.close()

    # @todo: Need message to display file name that has been restored which is held in future_file as a list.
    return jsonify({'message': "All original files are now restored."})


@app.route('/update_tariffs', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def update_tariffs():
    network_version, retail_version = start_up_procedures.update_tariffs()
    message = '''We have attempted to download the latest tariff version. Versions downloaded; Network: {}, Retail: {}. 
                 To use these versions please reset the active tariff database.'''.\
        format(network_version, retail_version)
    data = {'message': message}
    return jsonify(data)


@app.route('/open_tariff_info', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def open_tariff_info():
    request_details = request.get_json()
    tariff_id = data_interface.get_tariff('{}_tariff_selection_panel'.format(request_details['tariff_type']),
                                          request_details['name'])['Tariff ID']
    webbrowser.open('http://api.ceem.org.au/tariff-source/{}'.format(tariff_id), new=2)
    message = "If you have an active internet connection the relevant information should be displayed in a new tab"
    return jsonify({'message': message})


@app.route('/open_sample', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def open_sample():
    request_details = request.get_json()
    file_path = os.getcwd() + '\data\sample\{}.xlsx'.format(request_details['file_type'])
    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', file_path))
    elif platform.system() == 'Windows':  # Windows
        os.startfile(file_path)
    else:  # linux variants
        subprocess.call(('xdg-open', file_path))
    return jsonify({'message': "Done!".format(request.get_json())})


@app.route('/load_project', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def load_project():
    file = request.files['file']
    file.save('data/temp/temp.pkl')
    with open('data/temp/temp.pkl', "rb") as f:
        current_session.project_data = pickle.load(f)
    message = "Done!"
    also_return_a_list_of_cases_loaded = list(current_session.project_data.load_file_name_by_case.keys())
    return jsonify({'message': message, 'name': current_session.project_data.name,
                    'cases': also_return_a_list_of_cases_loaded})


@app.route('/save_project/<path:filename>')
@errors.parse_to_user_and_log(logger)
def save_project(filename):
    current_session.project_data.name = filename
    for the_file in os.listdir('data/temp'):
        file_path = os.path.join('data/temp', the_file)
        os.unlink(file_path)
    with open('data/temp/{}.tda_results'.format(filename), "wb") as f:
        pickle.dump(current_session.project_data, f)
    return send_from_directory('data/temp/', filename+'.tda_results', as_attachment=True)


@app.route('/current_project_name', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def current_project_name():
    return jsonify({'message': "Done!", 'name': current_session.project_data.name})


@app.route('/prepare_export_results', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def prepare_export_results():
    for the_file in os.listdir('data/temp'):
        file_path = os.path.join('data/temp', the_file)
        os.unlink(file_path)
    wb = Workbook()
    for case_name in current_session.project_data.load_file_name_by_case.keys():
        data_to_export = format_case_for_export.process_case(case_name, current_session.project_data)
        ws = wb.create_sheet(case_name)
        for row in data_to_export:
            ws.append(row,)
    wb.save('data/temp/results.xlsx')
    return jsonify({'message': "Done!", 'name': current_session.project_data.name})


@app.route('/export_results')
@errors.parse_to_user_and_log(logger)
def export_results():
    return send_from_directory('data/temp/', 'results.xlsx', as_attachment=True)


@app.route('/prepare_export_chart_data_to_csv', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def prepare_export_chart_data_to_csv():
    request_details = request.get_json()
    export_data = format_chart_data_for_export.plot_ly_to_pandas(request_details)
    export_data.to_csv('data/temp/chart_data.csv', index=False)
    return jsonify({'message': "Your export is done!"})


@app.route('/export_chart_data_to_csv')
@errors.parse_to_user_and_log(logger)
def export_chart_data_to_csv():
    return send_from_directory('data/temp/', 'chart_data.csv', as_attachment=True)


@app.route('/export_chart_data_to_clipboard', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def export_chart_data_to_clipboard():
    request_details = request.get_json()
    export_data = format_chart_data_for_export.plot_ly_to_pandas(request_details)
    export_data.to_clipboard(index=False)
    return jsonify({'message': "Your export is done!"})


@app.route('/validate_tariff_cell', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def validate_tariff_cell():
    request_details = request.get_json()
    cell_value = request_details['cell_value']
    column_name = request_details['column_name']
    message = validate_component_table_cell_values.validate_data(cell_value, column_name)
    return jsonify({'message': message})


@app.route('/restart_tool', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def restart_tool():
    current_session.__init__()
    check_load_2_demo_map()
    return jsonify("Done!")


def shutdown_server():
    print('called shutdown')
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    # shutdown_server()
    return 'Server shutting down...'


@errors.log(logger)
def on_start_up():
    start_up_procedures.update_nemosis_cache()
    start_up_procedures.update_tariffs()
    check_load_2_demo_map() # Fix load_2_demo_map if corrupted
    return None


if __name__ == '__main__':
    on_start_up()
    app.run(debug=True)
