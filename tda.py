from flask import Flask, render_template, request, jsonify
import os
import sys
import pandas as pd
import numpy as np
import helper_functions
import plotly
import json
from make_load_charts import chart_methods
from make_results_charts import singe_variable_chart, dual_variable_chart, single_case_chart
import data_interface
import Bill_Calc
from time import time
from datetime import datetime, timedelta

from tariff_processing import format_tariff_data_for_display, format_tariff_data_for_storage, \
    get_options_from_tariff_set, strip_tariff_to_single_component
import requests
from nemosis import data_fetch_methods
from make_price_charts import get_price_chart
from wholesale_energy import get_wholesale_prices, calc_wholesale_energy_costs
import pickle
from session_data import InMemoryData, ProjectData

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


@app.route('/tariff_selectors')
def tariff_selectors():
    return render_template('tariff_selectors.html')


@app.route('/tariff_table')
def tariff_table():
    return render_template('tariff_table.html')


@app.route('/load_names')
def load_names():
    # Get the list of load files for the user to choose from.
    names = []
    for file_name in os.listdir('data/load/'):
        names.append(file_name.split('.')[0])
    return jsonify(names)


@app.route('/get_tariff_set_options/<tariff_type>')
def get_tariff_set_options(tariff_type):
    # Get the versions of the tariff data base for the user to choose from.
    tariff_set_options = []
    # Determines if 'Network' or 'Retail' results are returned
    folder = 'data/{}_tariff_set_versions/'.format(tariff_type)
    for file_name in os.listdir(folder):
        tariff_set_options.append(file_name.split('.')[0])
    return jsonify(tariff_set_options)


@app.route('/set_tariff_set_in_use', methods=['POST'])
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
    return jsonify('done')


@app.route('/filtered_load_data', methods=['POST'])
def filtered_load_data():

    load_request = request.get_json()

    print('hi the down sample option is {}'.format(load_request['sample_fraction']))

    # Get raw load data.
    if load_request['file_name'] not in current_session.raw_data:
        current_session.raw_data[load_request['file_name']] = data_interface.get_load_table('data/load/', load_request['file_name'])

    # Filter data
    demo_info_file_name = data_interface.find_loads_demographic_file(load_request['file_name'])
    demo_info = pd.read_csv('data/demographics/' + demo_info_file_name, dtype=str)
    current_session.is_filtered, current_session.filtered_data = helper_functions.filter_load_data(current_session.raw_data[load_request['file_name']],
                                                                                                   demo_info,
                                                                                                   load_request['filter_options'])
    print(current_session.is_filtered)
    if not current_session.is_filtered:
        filtered_data = current_session.raw_data[load_request['file_name']]

    # Create the requested chart data if it does not already exist.
    if load_request['file_name'] not in current_session.raw_charts:
        current_session.raw_charts[load_request['file_name']] = {}
    # if load_request['chart_type'] not in raw_charts[load_request['file_name']]:

    if load_request['chart_type'] in ['Annual Average Profile', 'Daily kWh Histogram']:
        current_session.raw_charts[load_request['file_name']][load_request['chart_type']] = \
            chart_methods[load_request['chart_type']](current_session.raw_data[load_request['file_name']], current_session.filtered_data,
                                                      series_name=['All', 'Selected'])
    else:
        current_session.raw_charts[load_request['file_name']][load_request['chart_type']] = \
            chart_methods[load_request['chart_type']](current_session.filtered_data)

    #### prepare chart data and n_users
    chart_data = current_session.raw_charts[load_request['file_name']][load_request['chart_type']]
    if current_session.is_filtered:
        n_users = helper_functions.n_users(current_session.filtered_data)
    else:
        n_users = helper_functions.n_users(current_session.raw_data[load_request['file_name']])

    # If filtering has been applied also create the filtered chart data,
    # if filtered:
    #     print('filtered data ==========================')
    #     filtered_chart = chart_methods[load_request['chart_type']](filtered_data, series_name='Selected')
    #     # chart_data = raw_charts[load_request['file_name']][load_request['chart_type']]
    #     # chart_data.append(filtered_chart)
    #     # chart_data = [raw_charts[load_request['file_name']][load_request['chart_type']], filtered_chart]
    #     # n_users = data_interface.n_users(filtered_data)

    #     chart_data = filtered_chart
    #     n_users = data_interface.n_users(filtered_data)
    # else:
    #     chart_data = raw_charts[load_request['file_name']][load_request['chart_type']]
    #     n_users = data_interface.n_users(raw_data[load_request['file_name']])

    # Format as json.
    return_data = {"n_users": n_users, "chart_data": chart_data}
    return_data = json.dumps(return_data, cls=plotly.utils.PlotlyJSONEncoder)
    return return_data


@app.route('/get_case_default_name', methods=['GET'])
def get_case_default_name():
    # Default case names are of the format 'Case n'. If 'Case 1' is in use then try 'Case 2' etc until a case default
    # case name that is not in use is found.
    name = helper_functions.get_unique_default_case_name(current_session.load_by_case.keys())
    return jsonify(name)


@app.route('/add_case', methods=['POST'])
def add_case():
    # Using the currently active tariff (network tariff by default at the moment) calculate the bill for all load
    # profiles and save the results. Also save the other details associated with the case.

    # Unpack request details
    case_details = request.get_json()
    case_name = case_details['case_name']
    load_file_name = case_details['load_details']['file_name']
    filter_options = case_details['load_details']['filter_options']
    retail_tariff_name = case_details['retail_tariff_name']
    network_tariff_name = case_details['network_tariff_name']
    wholesale_year = case_details['wholesale_price_details']['year']
    wholesale_state = case_details['wholesale_price_details']['state']

    if network_tariff_name != 'None':
        network_tariff = data_interface.get_tariff('network_tariff_selection_panel', network_tariff_name)
        current_session.project_data.network_results_by_case[case_name] = Bill_Calc.bill_calculator(
            current_session.filtered_data.set_index('Datetime'), network_tariff)
        current_session.project_data.network_tariffs_by_case[case_name] = network_tariff

    if retail_tariff_name != 'None':
        retail_tariff = data_interface.get_tariff('retail_tariff_selection_panel', retail_tariff_name)
        current_session.project_data.retail_results_by_case[case_name] = Bill_Calc.bill_calculator(
            current_session.filtered_data.set_index('Datetime'), retail_tariff)
        current_session.project_data.retail_tariffs_by_case[case_name] = retail_tariff

    if (wholesale_year != 'None') & (wholesale_state != 'None'):
        price_data = get_wholesale_prices(wholesale_year, wholesale_state)
        current_session.project_data.wholesale_results_by_case[case_name] = calc_wholesale_energy_costs(
            price_data,  current_session.filtered_data.copy())
        current_session.project_data.wholesale_price_info_by_case[case_name] = {}
        current_session.project_data.wholesale_price_info_by_case[case_name]['year'] = wholesale_year
        current_session.project_data.wholesale_price_info_by_case[case_name]['state'] = wholesale_state

    # Save input data and settings associated with the case.
    current_session.load_by_case[case_name] = current_session.filtered_data
    current_session.project_data.load_file_name_by_case[case_name] = load_file_name
    current_session.project_data.load_n_users_by_case[case_name] = \
        helper_functions.n_users(current_session.filtered_data)
    current_session.project_data.filter_options_by_case[case_name] = filter_options
    return jsonify('done')


@app.route('/get_case_tariff', methods=['POST'])
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
def get_case_load():
    # Get the set of load profiles associated with a particular case.
    case_name = request.get_json()
    return jsonify({'n_users': current_session.project_data.load_n_users_by_case[case_name],
                    'database': current_session.project_data.load_file_name_by_case[case_name]})


@app.route('/get_case_demo_options', methods=['POST'])
def get_case_demo_options():
    # Get the demographic filtering options associated with a particular case.
    case_name = request.get_json()
    return jsonify(current_session.project_data.filter_options_by_case[case_name])


@app.route('/delete_case', methods=['POST'])
def delete_case():
    # Delete all data associated with a particular case.
    case_name = request.get_json()
    current_session.project_data.load_by_case.pop(case_name)
    if case_name in current_session.project_data.network_results_by_case.keys():
        current_session.project_data.network_results_by_case.pop(case_name)
    if case_name in current_session.project_data.retail_results_by_case.keys():
        current_session.project_data.retail_results_by_case.pop(case_name)
    if case_name in current_session.project_data.retail_tariffs_by_case.keys():
        current_session.project_data.retail_tariffs_by_case.pop(case_name)
    if case_name in current_session.project_data.network_tariffs_by_case.keys():
        current_session.project_data.network_tariffs_by_case.pop(case_name)
    return jsonify('done')


@app.route('/get_single_variable_chart', methods=['POST'])
def get_single_variable_chart():
    details = request.get_json()
    chart_name = details['chart_name']
    case_names = details['case_names']
    results_to_plot = helper_functions.get_results_subset_to_plot(
        case_names,
        current_session.project_data.retail_results_by_case,
        current_session.project_data.network_results_by_case,
        current_session.project_data.wholesale_results_by_case)
    return singe_variable_chart(chart_name, results_to_plot)


@app.route('/get_dual_variable_chart', methods=['POST'])
def get_dual_variable_chart():
    details = request.get_json()
    x_axis = details['x_axis']
    y_axis = details['y_axis']
    case_names = details['case_names']

    # Other cool variables we should totally use!
    include_summer = details['include_summer']  # boolean
    include_autumn = details['include_autumn']  # boolean
    include_winter = details['include_winter']  # boolean
    include_spring = details['include_spring']  # boolean
    x_axis_n_peaks = details['x_axis_n_peaks']  # string
    x_axis_n_peaks = details['y_axis_n_peaks']  # string
    x_axis_one_peak_per_day = details['x_axis_one_peak_per_day']  # boolean
    y_axis_one_peak_per_day = details['y_axis_one_peak_per_day']  # boolean

    results_to_plot = helper_functions.get_results_subset_to_plot(case_names,
                                                                  current_session.project_data.retail_results_by_case,
                                                                  current_session.project_data.network_results_by_case,
                                                                  current_session.project_data.wholesale_results_by_case)
    return dual_variable_chart(results_to_plot, x_axis, y_axis)


@app.route('/get_single_case_chart', methods=['POST'])
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

    return single_case_chart(chart_name, results_to_plot)


@app.route('/get_demo_options/<name>')
def get_demo_options(name):
    demo_file_name = data_interface.find_loads_demographic_file(name)

    if demo_file_name != '' and demo_file_name in os.listdir('data/demographics/'):
        demo = pd.read_csv('data/demographics/' + demo_file_name)
        demo_options = helper_functions.get_demographic_options_from_demo_file(demo)
    else:
        demo_options = {'actual_names': [], "display_names": {}, "options": {}}

    return jsonify(demo_options)


@app.route('/wholesale_price_options', methods=['POST'])
def wholesale_price_options():
    # First year to access data from.
    year = 2012
    # Month to check for data.
    month = 12
    # url to check for data at.
    aemo_data_url = 'http://www.nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/{}/MMSDM_{}_{}'
    # Status to keep checking for new data on.
    last_year = 'complete'
    # Add years to the list that the user can select from where that year has an AMEO
    years = []
    while last_year == 'complete':
        url_to_check = aemo_data_url.format(year, year, month)
        r = requests.get(url_to_check)
        if r.status_code != 404:
            years.append(year)
            year += 1
        else:
            last_year = 'not complete'
    # Hard coded regions that the user can select from.
    states = ['NSW', "VIC", 'TAS', 'QLD', 'SA']
    return jsonify({'states': states, 'years': years})


@app.route('/wholesale_prices', methods=['POST'])
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
def get_wholesale_price_info():
    case_name = request.json
    if case_name in current_session.project_data.wholesale_price_info_by_case.keys():
        info = {'state': current_session.project_data.wholesale_price_info_by_case[case_name]['state'],
                'year': current_session.project_data.wholesale_price_info_by_case[case_name]['year']}
    else:
        info = 'None'
    return jsonify(info)


@app.route('/add_end_user_tech', methods=['POST'])
def add_end_user_tech():
    details = request.json
    solar_pen = details['solar_inputs']['penetration']
    return jsonify('done')


@app.route('/tariff_options', methods=['POST'])
def tariff_options():
    request_details = request.get_json()
    tariff_filter_state = request_details['current_options']
    tariff_panel = request_details['tariff_panel']
    # Open the tariff data set.
    tariffs = data_interface.get_tariffs(tariff_panel)
    # Given the tariff set and the current state of the filter find the remain options for the gui filters
    options = get_options_from_tariff_set(tariffs, tariff_filter_state)
    return jsonify(options)


@app.route('/tariff_json', methods=['POST'])
def tariff_json():
    request_details = request.get_json()
    selected_tariff = data_interface.get_tariff(request_details['tariff_panel'],
                                                request_details['tariff_name'])
    selected_tariff = format_tariff_data_for_display(selected_tariff)
    return jsonify(selected_tariff)


@app.route('/save_tariff', methods=['POST'])
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
    return jsonify("saved")


@app.route('/delete_tariff', methods=['POST'])
def delete_tariff():
    request_details = request.get_json()
    # Open the tariff data set.
    if request_details['tariff_panel'] == 'network_tariff_selection_panel':
        file_name = 'NetworkTariffs'
    else:
        file_name = 'RetailTariffs'

    for file_type in ['', 'UserDefined']:
        with open('data/{}{}.json'.format(file_type, file_name), 'rt') as json_file:
            tariffs = json.load(json_file)

        for i, tariff in enumerate(tariffs):
            if request_details['tariff_name'] == tariff['Name']:
                del tariffs[i]

        with open('data/{}{}.json'.format(file_type, file_name), 'wt') as json_file:
            json.dump(tariffs, json_file)

    return jsonify("deleted")


@app.route('/import_load_data', methods=['POST'])
def import_load_data():
    return jsonify("No python code for importing data yet!")


@app.route('/delete_load_data', methods=['POST'])
def delete_load_data():
    request_details = request.get_json()
    print('I know you want to delete {}'.format(request_details['name']))
    return jsonify("No python code for deleting data yet!")


@app.route('/restore_original_data_set', methods=['POST'])
def restore_original_data_set():
    return jsonify("No python code for restoring data yet!")


@app.route('/update_tariffs', methods=['POST'])
def update_tariffs():
    return jsonify("No python code for updating tariffs yet!")


@app.route('/open_tariff_info', methods=['POST'])
def open_tariff_info():
    return jsonify("No python code for opening tariff info yet!")


@app.route('/create_synthetic_network_load', methods=['POST'])
def create_synthetic_network_load():
    message = "No python code for creating synthetic network load yet! But we have returned a dummy name to add!"
    dummy_name_to_add_as_option_in_ui = "not real option"
    return jsonify({'message': message, 'name': dummy_name_to_add_as_option_in_ui})


@app.route('/open_sample', methods=['POST'])
def open_sample():
    print('open sample for data: {}'.format(request.get_json()))
    return jsonify("No python code for opening sample {} data yet!".format(request.get_json()))


@app.route('/load_project', methods=['POST'])
def load_project():
    file_path = helper_functions.get_file_to_load_from_user()
    with open(file_path, "rb") as f:
        current_session.project_data = pickle.load(f)
    message = "Done!"
    current_session.project_data.name = file_path.split('/')[-1][:-4]
    also_return_a_list_of_cases_loaded = list(current_session.project_data.load_file_name_by_case.keys())
    return jsonify({'message': message, 'name': current_session.project_data.name, 'cases': also_return_a_list_of_cases_loaded})


@app.route('/save_project', methods=['POST'])
def save_project():
    if current_session.project_data.name == '':
        file_path = helper_functions.get_save_name_from_user()
        if file_path[-4:] != '.pkl':
            file_path = file_path + '.pkl'
    else:
        file_path = current_session.project_data.name + '.pkl'
    with open(file_path, "wb") as f:
        pickle.dump(current_session.project_data, f)
    return jsonify("Done!")


@app.route('/save_project_as', methods=['POST'])
def save_project_as():
    file_path = helper_functions.get_save_name_from_user()
    if file_path[-4:] != '.pkl':
        file_path = file_path + '.pkl'
    current_session.project_data.name = file_path.split('/')[-1][:-4]
    with open(file_path, "wb") as f:
        pickle.dump(current_session.project_data, f)
    return jsonify({'message': 'Done!', 'name': current_session.project_data.name})


@app.route('/delete_project', methods=['POST'])
def delete_project():
    return jsonify("No python code for deleting projects as yet!")


@app.route('/restart_tool', methods=['POST'])
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


if __name__ == '__main__':
    app.run()

    # init_gui(app, width=1200, height=800, window_title='TDA')  # This one runs it as a standalone app
