from flask import Flask, render_template, request, jsonify
import os
from pyfladesk import init_gui
import sys
import pandas as pd
import feather
from time import time
import helper_functions
import plotly
import plotly.graph_objs as go
import json
from make_load_charts import chart_methods

data_dict = {}

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
    return render_template('index.html', my_name="Nick")


# Here you go to http://127.0.0.1:5000/data
@app.route('/data')
def data():
    return jsonify(
        {'data': [1, 2, 3, 4, 5]}
    )


@app.route('/load_names')
def load_names():
    load_names = []
    for file_name in os.listdir('data/'):
        load_names.append(file_name)
    return jsonify(load_names)

@app.route('/n_users/<name>')
def n_users(name):
    if 'filtered' in data_dict[name]:
        n_users = len(set(data_dict[name]['filtered']['CUSTOMER_KEY']))
    else:
        n_users = len(set(data_dict[name]['raw']['CUSTOMER_KEY']))
    return str(n_users)

@app.route('/filtered_load_data', methods=['POST'])
def filtered_load_data():
    t0 = time()
    load_request = request.get_json()
    if load_request['file_name'] not in data_dict:
        temp_load = pd.read_csv('data/' + load_request['file_name'])
        t0 = time()
        temp_load['READING_DATETIME'] = pd.to_datetime(temp_load['READING_DATETIME'])
        print('time format datetime {}'.format(time() - t0))
        temp_load = pd.melt(temp_load, id_vars=['READING_DATETIME'],
                            value_vars=[x for x in temp_load.columns if x != 'READING_DATETIME'],
                            var_name='CUSTOMER_KEY', value_name='Energy_kWh')
        data_dict[load_request['file_name']] = {}
        data_dict[load_request['file_name']]['raw'] = temp_load
    else:
        temp_load = data_dict[load_request['file_name']]['raw']

    print('time get load {}'.format(time()-t0))
    t0 = time()

    # Create filter set of customer keys
    demo_info_file_name = helper_functions.find_loads_demographic_file(load_request['file_name'])
    demo_info = pd.read_csv('data/' + demo_info_file_name, dtype=str)
    filter = False
    for column_name, selected_options in load_request['filter_options'].items():
        if 'All' not in selected_options:
            demo_info = demo_info[demo_info[column_name].isin(selected_options)]
            filter = True
    print('time to find cus keys {}'.format(time() - t0))
    # Create the requested chart data if it does not already exist.
    if 'charts' not in data_dict[load_request['file_name']]:
        data_dict[load_request['file_name']]['charts'] = {}
    if 'raw' not in data_dict[load_request['file_name']]['charts']:
        data_dict[load_request['file_name']]['charts']['raw'] = {}
    if load_request['chart_type'] not in data_dict[load_request['file_name']]['charts']['raw']:
        data_dict[load_request['file_name']]['charts']['raw'][load_request['chart_type']] = \
            chart_methods[load_request['chart_type']](data_dict[load_request['file_name']]['raw'],
                                                      series_name='All users')

    # If filtering has been applied also create the filtered chart data,
    if filter:
        t1 = time()
        data_dict[load_request['file_name']]['filtered'] = \
            temp_load[temp_load['CUSTOMER_KEY'].isin(demo_info['CUSTOMER_KEY'])]
        print('time to find cus keys {}'.format(time() - t1))
        if 'filtered' not in data_dict[load_request['file_name']]['charts']:
            data_dict[load_request['file_name']]['charts']['filtered'] = {}
        data_dict[load_request['file_name']]['charts']['filtered'][load_request['chart_type']] = \
            chart_methods[load_request['chart_type']](data_dict[load_request['file_name']]['filtered'],
                                                      series_name='Selected Users')
        chart_data = [data_dict[load_request['file_name']]['charts']['raw'][load_request['chart_type']],
                      data_dict[load_request['file_name']]['charts']['filtered'][load_request['chart_type']]]
    else:
        chart_data = [data_dict[load_request['file_name']]['charts']['raw'][load_request['chart_type']]]
    graph_json = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    print('time to filter and make graph {}'.format(time() - t0))
    return graph_json


@app.route('/demo_options/<name>')
def demo_options(name):
    demo_config_file_name = helper_functions.find_loads_demographic_config_file(name)
    demo_file_name = helper_functions.find_loads_demographic_file(name)
    if demo_config_file_name != '' and demo_config_file_name in os.listdir('data/'):
        demo_config = pd.read_csv('data/'+demo_config_file_name)
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


if __name__ == '__main__':
    app.run(debug=True)

    #init_gui(app, width=1200, height=800, window_title='TDA')  # This one runs it as a standalone app