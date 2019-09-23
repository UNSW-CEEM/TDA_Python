from flask import Flask, render_template, request, jsonify
import os
import sys
import pandas as pd
import helper_functions
import plotly
import json
from make_load_charts import chart_methods
from make_results_charts import singe_variable_chart, dual_variable_chart, single_case_chart
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
    chart_type = load_request['chart_type']
    current_session.filter_state = load_request['filter_options']

    print('hi the down sample option is {}'.format(load_request['sample_fraction']))

    # Filter data
    demo_info_file_name = data_interface.find_loads_demographic_file(file_name)
    demo_info = pd.read_csv('data/demographics/' + demo_info_file_name, dtype=str)
    demo_info = helper_functions.add_missing_customer_keys_to_demo_file_with_nan_values(
        current_session.raw_data[file_name], demo_info)

    current_session.filtered_demo_info, current_session.is_filtered = \
        helper_functions.filter_demo_info(demo_info, load_request['filter_options'])
    current_session.filtered_data = helper_functions.filter_load_data(
        current_session.raw_data[file_name], current_session.filtered_demo_info)

    # Create the requested chart data if it does not already exist.
    if file_name not in current_session.raw_charts:
        current_session.raw_charts[file_name] = {}

    # prepare chart data and n_users
    current_session.filtered_charts = {file_name: {}}
    
    if chart_type not in current_session.raw_charts[file_name]:
        if chart_type in ['Annual Average Profile', 'Daily kWh Histogram']:
            current_session.raw_charts[file_name][chart_type] = \
                chart_methods[chart_type](current_session.raw_data[file_name],
                                          current_session.filtered_data, series_name=['All'])
        else:
            current_session.raw_charts[file_name][chart_type] = \
                chart_methods[chart_type](current_session.raw_data[file_name])

    if current_session.is_filtered:
        if chart_type in ['Annual Average Profile', 'Daily kWh Histogram']:
            current_session.filtered_charts[file_name][chart_type] = \
                chart_methods[chart_type](current_session.raw_data[file_name], current_session.filtered_data,
                                          series_name=['All', 'Selected'])
        else:
            current_session.filtered_charts[file_name][chart_type] = \
                chart_methods[chart_type](current_session.filtered_data)

        chart_data = current_session.filtered_charts[file_name][chart_type]
        n_users = helper_functions.n_users(current_session.filtered_data)
    else:
        chart_data = current_session.raw_charts[file_name][chart_type]
        n_users = helper_functions.n_users(current_session.raw_data[file_name])

    # Format as json.
    return_data = {"n_users": n_users, "chart_data": chart_data}
    return_data = json.dumps(return_data, cls=plotly.utils.PlotlyJSONEncoder)
    return return_data


@app.route('/net_load_chart_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def net_load_chart_data():
    # TODO: Update this function to produce the actual plots of net load we want.
    load_request = request.get_json()
    file_name = current_session.raw_data_name
    chart_type = load_request['chart_type']
    if chart_type in ['Annual Average Profile', 'Daily kWh Histogram']:
        chart_data = chart_methods[chart_type](current_session.raw_data[file_name],
                                               current_session.filtered_data,
                                               series_name=['All', 'Selected'])
    else:
        chart_data = chart_methods[chart_type](current_session.filtered_data)

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

    # Save demographic info for case
    current_session.project_data.demographic_info_by_case[case_name] = current_session.filtered_demo_info

    if network_tariff_name != 'None':
        network_tariff = data_interface.get_tariff('network_tariff_selection_panel', network_tariff_name)
        network_results = Bill_Calc.bill_calculator(current_session.filtered_data.set_index('Datetime'), network_tariff)
        network_results.index.name = 'CUSTOMER_KEY'
        network_results = network_results.reset_index()
        current_session.project_data.network_results_by_case[case_name] = network_results
        current_session.project_data.network_tariffs_by_case[case_name] = network_tariff

    if retail_tariff_name != 'None':
        retail_tariff = data_interface.get_tariff('retail_tariff_selection_panel', retail_tariff_name)
        retail_results = Bill_Calc.bill_calculator(current_session.filtered_data.set_index('Datetime'), retail_tariff)
        retail_results.index.name = 'CUSTOMER_KEY'
        retail_results = retail_results.reset_index()
        current_session.project_data.retail_results_by_case[case_name] = retail_results
        current_session.project_data.retail_tariffs_by_case[case_name] = retail_tariff

    if (wholesale_year != 'None') & (wholesale_state != 'None'):
        price_data = get_wholesale_prices(wholesale_year, wholesale_state)
        wholesale_results = calc_wholesale_energy_costs(price_data,  current_session.filtered_data.copy())
        wholesale_results.index.name = 'CUSTOMER_KEY'
        wholesale_results = wholesale_results.reset_index()
        current_session.project_data.wholesale_results_by_case[case_name] = wholesale_results
        current_session.project_data.wholesale_price_info_by_case[case_name] = {}
        current_session.project_data.wholesale_price_info_by_case[case_name]['year'] = wholesale_year
        current_session.project_data.wholesale_price_info_by_case[case_name]['state'] = wholesale_state

    # Save input data and settings associated with the case.
    current_session.load_by_case[case_name] = current_session.filtered_data
    current_session.project_data.load_file_name_by_case[case_name] = load_file_name
    current_session.project_data.load_n_users_by_case[case_name] = \
        helper_functions.n_users(current_session.filtered_data)
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
    file_name = details['load_details']['file_name']
    results_to_plot = helper_functions.get_results_subset_to_plot(case_names, 
                                                                  current_session.project_data.retail_results_by_case,
                                                                  current_session.project_data.network_results_by_case,
                                                                  current_session.project_data.wholesale_results_by_case)
    load_and_results_to_plot = {'results': results_to_plot, 'load': current_session.load_by_case,
                                'network_load': current_session.raw_data[current_session.raw_data_name]}

    return dual_variable_chart(load_and_results_to_plot, details)


@app.route('/get_single_case_chart', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def get_single_case_chart():
    details = request.get_json()
    print(details)
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

    load_and_results_to_plot = {'results': results_to_plot, 'load': current_session.load_by_case[case_name]}

    return single_case_chart(chart_name, load_and_results_to_plot)


@app.route('/get_demo_options/<name>')
@errors.parse_to_user_and_log(logger)
def get_demo_options(name):
    demo_file_name = data_interface.find_loads_demographic_file(name)

    if demo_file_name != '' and demo_file_name in os.listdir('data/demographics/'):
        demo = pd.read_csv('data/demographics/' + demo_file_name, dtype=str)
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
    current_session.filtered_data = \
        end_user_tech.calc_net_profiles(current_session.filtered_data, current_session.end_user_tech_sample)
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
        filtered_data = raw_data.loc[:, ['Datetime'] + current_session.end_user_tech_sample['customer_keys']]
        current_session.filtered_data = end_user_tech.calc_net_profiles(filtered_data,
                                                                        current_session.end_user_tech_sample)
        current_session.filter_state = current_session.end_user_tech_sample['load_details']['filter_options']
        return_data = jsonify({'message': 'Done!', 'tech_inputs': current_session.end_user_tech_sample['tech_inputs']})
    else:
        return_data = jsonify({'error': 'You do not have the required load data to use this tech sample.'})

    return return_data


@app.route('/calc_sample_net_load_profiles', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def calc_sample_net_load_profiles():
    details = request.json
    current_session.end_user_tech_sample = end_user_tech.update_sample(current_session.end_user_tech_sample, details)
    current_session.filtered_data = \
        end_user_tech.calc_net_profiles(current_session.filtered_data, current_session.end_user_tech_sample)
    return jsonify({'message': 'done'})


@app.route('/save_end_user_tech_sample', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def save_end_user_tech_sample():
    details = request.json
    current_session.end_user_tech_sample = end_user_tech.update_sample(current_session.end_user_tech_sample, details)
    file_path = helper_functions.get_save_name_from_user('TDA tech sample', '.tda_tech_sample')
    if file_path != '':
        file_path = helper_functions.add_file_extension_if_needed(file_path, '.tda_tech_sample')
        with open(file_path, "wb") as f:
            pickle.dump(current_session.end_user_tech_sample, f)
        message = 'saved'
    else:
        message = 'nothing saved'
    return jsonify({'message': message})


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
def import_load_data():
    
    return jsonify({'message': "No python code for importing data yet!"})


@app.route('/delete_load_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def delete_load_data():
    request_details = request.get_json()
    print('I know you want to delete {}'.format(request_details['name']))
    return jsonify({'message': "No python code for deleting data yet!"})


@app.route('/restore_original_data_set', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def restore_original_data_set():
    return jsonify({'message': "No python code for restoring data yet!"})


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
    return jsonify({'message': "No python code for opening tariff info yet!"})


@app.route('/import_load', methods=['POST'])
def import_load():
    message = "No python code for creating synthetic network load yet! But we have returned a dummy name to add!"
    dummy_name_to_add_as_option_in_ui = "not real option"
    return jsonify({'message': message, 'name': dummy_name_to_add_as_option_in_ui})


@app.route('/open_sample', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def open_sample():
    print('open sample for data: {}'.format(request.get_json()))
    return jsonify({'message': "No python code for opening sample {} data yet!".format(request.get_json())})


@app.route('/load_project', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def load_project():
    file_path = helper_functions.get_file_to_load_from_user('TDA results file', '.tda_results')
    with open(file_path, "rb") as f:
        current_session.project_data = pickle.load(f)
    message = "Done!"
    current_session.project_data.name = helper_functions.get_project_name_from_file_path(file_path)
    also_return_a_list_of_cases_loaded = list(current_session.project_data.load_file_name_by_case.keys())
    return jsonify({'message': message, 'name': current_session.project_data.name, 'cases': also_return_a_list_of_cases_loaded})


@app.route('/save_project', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def save_project():
    if current_session.project_data.name == '':
        file_path = helper_functions.get_save_name_from_user()
        file_path = helper_functions.add_file_extension_if_needed(file_path)
    else:
        file_path = current_session.project_data.name + '.tda_results'
    with open(file_path, "wb") as f:
        pickle.dump(current_session.project_data, f)
    return jsonify({'message': "Done!"})


@app.route('/save_project_as', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def save_project_as():
    file_path = helper_functions.get_save_name_from_user('TDA results file', '.tda_results')
    file_path = helper_functions.add_file_extension_if_needed(file_path, '.tda_results')
    current_session.project_data.name = helper_functions.get_project_name_from_file_path(file_path)
    with open(file_path, "wb") as f:
        pickle.dump(current_session.project_data, f)
    return jsonify({'message': 'Done!', 'name': current_session.project_data.name})


@app.route('/delete_project', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def delete_project():
    return jsonify({'message': "No python code for deleting projects as yet!"})


@app.route('/export_results', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def export_results():
    file_path = helper_functions.get_save_name_from_user('excel file', '.xlsx')
    file_path = helper_functions.add_file_extension_if_needed(file_path, '.xlsx')
    wb = Workbook()
    for case_name in current_session.project_data.load_file_name_by_case.keys():
        data_to_export = format_case_for_export.process_case(case_name, current_session.project_data)
        ws = wb.create_sheet(case_name)
        for row in data_to_export:
            ws.append(row,)
    wb.save(file_path)
    return jsonify({'message': "Done!"})


@app.route('/export_chart_data', methods=['POST'])
@errors.parse_to_user_and_log(logger)
def export_chart_data():
    request_details = request.get_json()
    export_data = format_chart_data_for_export.plot_ly_to_pandas(request_details)
    if request_details['export_type'] == 'csv':
        file_path = helper_functions.get_save_name_from_user('csv file', '.csv')
        file_path = helper_functions.add_file_extension_if_needed(file_path, '.csv')
        export_data.to_csv(file_path, index=False)
    elif request_details['export_type'] == 'clipboard':
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
    return jsonify("Done!")


def shutdown_server():
    print('called shutdown')
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    #shutdown_server()
    return 'Server shutting down...'


@errors.log(logger)
def on_start_up():
    start_up_procedures.update_nemosis_cache()
    start_up_procedures.update_tariffs()
    return None


if __name__ == '__main__':
    on_start_up()
    app.run()
