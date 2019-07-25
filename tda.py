from flask import Flask, render_template, request, jsonify
import os
import sys
import pandas as pd
import helper_functions
import plotly
import json
from make_load_charts import chart_methods
from make_results_charts import results_chart_methods, dual_variable_chart_method, single_case_chart_methods
import data_interface
import Bill_Calc
from time import time


raw_data = {}
raw_charts = {}
filtered_charts = {}
results_by_case = {}
load_by_case = {}
tariff_by_case = {}
load_file_name_by_case = {}
load_n_users_by_case = {}
filter_options_by_case = {}


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


@app.route('/tariff_panel_header')
def tariff_panel_header():
    return render_template('tariff_panel_header.html')


@app.route('/load_names')
def load_names():
    load_names = []
    for file_name in os.listdir('data/'):
        load_names.append(file_name)
    return jsonify(load_names)


@app.route('/filtered_load_data', methods=['POST'])
def filtered_load_data():

    load_request = request.get_json()

    # Get raw load data.
    if load_request['file_name'] not in raw_data:
        raw_data[load_request['file_name']] = data_interface.get_load_table('data/', load_request['file_name'])


    filtered, filtered_data = data_interface.filter_load_data(raw_data[load_request['file_name']],
                                                              load_request['file_name'],
                                                              load_request['filter_options'])

    # Create the requested chart data if it does not already exist.
    if load_request['file_name'] not in raw_charts:
        raw_charts[load_request['file_name']] = {}
    if load_request['chart_type'] not in raw_charts[load_request['file_name']]:
        raw_charts[load_request['file_name']][load_request['chart_type']] = \
            chart_methods[load_request['chart_type']](raw_data[load_request['file_name']], series_name='All')

    # If filtering has been applied also create the filtered chart data,
    if filtered:
        filtered_chart = chart_methods[load_request['chart_type']](filtered_data, series_name='Selected')
        chart_data = [raw_charts[load_request['file_name']][load_request['chart_type']], filtered_chart]
        n_users = data_interface.n_users(filtered_data)
    else:
        chart_data = [raw_charts[load_request['file_name']][load_request['chart_type']]]
        n_users = data_interface.n_users(raw_data[load_request['file_name']])


    # Format as json.
    return_data = {"n_users": n_users, "chart_data": chart_data}
    return_data = json.dumps(return_data, cls=plotly.utils.PlotlyJSONEncoder)
    return return_data


@app.route('/get_case_default_name', methods=['GET'])
def get_case_default_name():
    base_name = "Case "
    not_unique = True
    number = 1
    while not_unique:
        test_name = base_name + str(number)
        if test_name not in results_by_case.keys():
            break
        number += 1
    return jsonify(test_name)


@app.route('/add_case', methods=['POST'])
def add_case():
    case_details = request.get_json()
    case_name = case_details['case_name']
    load_file_name = case_details['load_details']['file_name']
    filter_options = case_details['load_details']['filter_options']
    requested_tariff = case_details['tariff_name']

    filtered, load_data = data_interface.filter_load_data(raw_data[load_file_name], load_file_name, filter_options)

    selected_tariff = data_interface.get_tariff('network_tariff_selection_panel', requested_tariff)
    selected_tariff = helper_functions.strip_tariff_to_single_component(selected_tariff, case_details['component'])

    results_by_case[case_name] = Bill_Calc.bill_calculator(load_data.set_index('Datetime'), selected_tariff)
    load_by_case[case_name] = load_data
    tariff_by_case[case_name] = selected_tariff
    load_file_name_by_case[case_name] = load_file_name
    load_n_users_by_case[case_name] = data_interface.n_users(load_data)
    filter_options_by_case[case_name] = filter_options
    return jsonify('done')


@app.route('/get_case_tariff', methods=['POST'])
def get_case_tariff():
    case_name = request.get_json()
    tariff = tariff_by_case[case_name]
    tariff = helper_functions.format_tariff_data_for_display(tariff)
    return jsonify(tariff)


@app.route('/get_case_load', methods=['POST'])
def get_case_load():
    case_name = request.get_json()
    return jsonify({'n_users': load_n_users_by_case[case_name], 'database': load_file_name_by_case[case_name]})


@app.route('/get_case_demo_options', methods=['POST'])
def get_case_demo_options():
    case_name = request.get_json()
    return jsonify(filter_options_by_case[case_name])


@app.route('/delete_case', methods=['POST'])
def delete_case():
    case_name = request.get_json()
    results_by_case.pop(case_name)
    load_by_case.pop(case_name)
    tariff_by_case.pop(case_name)
    return jsonify('done')


@app.route('/get_single_variable_chart', methods=['POST'])
def get_single_variable_chart():
    details = request.get_json()
    chart_name = details['chart_name']
    case_names = details['case_names']
    chart_data = []
    for name in case_names:
        chart_data.append(results_chart_methods[chart_name](results_by_case[name], name))
    return_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return return_data


@app.route('/get_dual_variable_chart', methods=['POST'])
def get_dual_variable_chart():
    details = request.get_json()
    x_axis = details['x_axis']
    y_axis = details['y_axis']
    case_names = details['case_names']
    chart_data = []
    for name in case_names:
        chart_data.append(dual_variable_chart_method(results_by_case[name], x_axis, y_axis, name))
    return_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return return_data


@app.route('/get_single_case_chart', methods=['POST'])
def get_single_case_chart():
    details = request.get_json()
    chart_name = details['chart_name']
    case_name = details['case_name']
    chart_data = single_case_chart_methods[chart_name](results_by_case[case_name])
    return_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return return_data


@app.route('/demo_options/<name>')
def demo_options(name):
    demo_config_file_name = helper_functions.find_loads_demographic_config_file(name)
    demo_file_name = helper_functions.find_loads_demographic_file(name)
    if demo_config_file_name != '' and demo_config_file_name in os.listdir('data/'):
        demo_config = pd.read_csv('data/' + demo_config_file_name)
        columns_to_use = demo_config[demo_config['use'] == 1]
        n = len(columns_to_use['actual_names']) if len(columns_to_use['actual_names']) < 10 else 10
        actual_names = list(columns_to_use['actual_names'].iloc[:n])
        display_names = list(columns_to_use['display_names'])
    elif demo_file_name != '' and demo_file_name in os.listdir('data/'):
        demo = pd.read_csv('data/' + demo_file_name)
        n = len(demo.columns) if len(demo.columns) < 11 else 11
        actual_names = list(demo.columns[1:n])
        display_names = list(demo.columns[1:n])
    else:
        actual_names = []
        display_names = []

    options = {}
    display_names_dict = {}
    for name, display_name in zip(actual_names, display_names):
        options[name] = ['All'] + list([str(val) for val in demo[name].unique()])
        display_names_dict[name] = display_name

    return jsonify({'actual_names': actual_names, "display_names": display_names_dict, "options": options})


@app.route('/tariff_options', methods=['POST'])
def tariff_options():
    request_details = request.get_json()
    tariff_filter_state = request_details['current_options']
    tariff_panel = request_details['tariff_panel']
    # Open the tariff data set.
    tariffs = data_interface.get_tariffs(tariff_panel)

    # Define the options to update.
    option_types = {'.select_tariff_state': 'State',
                    '.select_tariff_provider': 'Provider',
                    '.select_tariff_type': 'Type',
                    '.select_tariff': 'Name'}
    options = {'.select_tariff_state': [],
               '.select_tariff_provider': [],
               '.select_tariff_type': [],
               '.select_tariff': []}

    # Look at each tariff build up a set of possible options for each option type.
    for tariff in tariffs:
        # Decide if current tariff meets current filters
        add_tariff_as_option = True
        for option_type, option_name in option_types.items():
            if ((tariff_filter_state[option_type] != 'Select1') &
                (tariff_filter_state[option_type] != tariff[option_name])) & \
                (option_name != 'Name'):
                add_tariff_as_option = False
        # If the current tariff meets the all the filters add its properties to the allowed options.
        for option_type, option_name in option_types.items():
            if add_tariff_as_option and tariff[option_name] not in options[option_type]:
                options[option_type].append(tariff[option_name])

    return jsonify(options)


@app.route('/tariff_json', methods=['POST'])
def tariff_json():
    request_details = request.get_json()
    selected_tariff = data_interface.get_tariff(request_details['tariff_panel'], request_details['tariff_name'])
    selected_tariff = helper_functions.format_tariff_data_for_display(selected_tariff)
    return jsonify(selected_tariff)


@app.route('/save_tariff', methods=['POST'])
def save_tariff():
    tariff_to_save = helper_functions.format_tariff_data_for_storage(request.get_json())
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

    #init_gui(app, width=1200, height=800, window_title='TDA')  # This one runs it as a standalone app
