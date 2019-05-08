from flask import Flask, render_template, request, jsonify
import os
import sys
import pandas as pd
import helper_functions
import plotly
import json
from make_load_charts import chart_methods
import data_interface
from time import time


raw_data = {}
filtered_data = {}
raw_charts = {}
filtered_charts = {}

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

@app.route('/load_names')
def load_names():
    load_names = []
    for file_name in os.listdir('data/'):
        load_names.append(file_name)
    return jsonify(load_names)


@app.route('/n_users/<name>')
def n_users(name):
    if name in filtered_data and filtered_data[name] is not None:
        n = len(set(filtered_data[name]['CUSTOMER_KEY']))
    else:
        n = len(set(raw_data[name]['CUSTOMER_KEY']))
    return str(n)


@app.route('/filtered_load_data', methods=['POST'])
def filtered_load_data():
    t0 = time()
    load_request = request.get_json()
    # Get raw load data.
    t1 = time()
    if load_request['file_name'] not in raw_data:
        raw_data[load_request['file_name']] = data_interface.get_load_table_alt('data/', load_request['file_name'])
    print('Time get load data {}'.format(time() - t1))
    # Create filtered set of customer keys.
    demo_info_file_name = helper_functions.find_loads_demographic_file(load_request['file_name'])
    demo_info = pd.read_csv('data/' + demo_info_file_name, dtype=str)
    filtered = False
    for column_name, selected_options in load_request['filter_options'].items():
        if 'All' not in selected_options:
            demo_info = demo_info[demo_info[column_name].isin(selected_options)]
            filtered = True

    # Create the requested chart data if it does not already exist.
    if load_request['file_name'] not in raw_charts:
        raw_charts[load_request['file_name']] = {}
    if load_request['chart_type'] not in raw_charts[load_request['file_name']]:
        raw_charts[load_request['file_name']][load_request['chart_type']] = \
            chart_methods[load_request['chart_type']](raw_data[load_request['file_name']], series_name='All')

    # If filtering has been applied also create the filtered chart data,
    if filtered:
        filtered_data[load_request['file_name']] = \
            raw_data[load_request['file_name']][raw_data[load_request['file_name']]['CUSTOMER_KEY'].
                isin(demo_info['CUSTOMER_KEY'])]
        filtered_chart = chart_methods[load_request['chart_type']](filtered_data[load_request['file_name']],
                                                                   series_name='Selected')
        chart_data = [raw_charts[load_request['file_name']][load_request['chart_type']], filtered_chart]
    else:
        filtered_data[load_request['file_name']] = None
        chart_data = [raw_charts[load_request['file_name']][load_request['chart_type']]]

    # Format as json.
    graph_json = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    print('Total time in plot filtered load {}'.format(time()-t0))
    return graph_json


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
