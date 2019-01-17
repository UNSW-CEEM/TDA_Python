from flask import Flask, render_template, request, jsonify
import os
from pyfladesk import init_gui
import sys
import pandas as pd
import feather
import time
import numpy as np
from datetime import timedelta

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


@app.route('/load_load/<name>')
def load_load(name):
    load = feather.read_dataframe('data/'+name)
    load['READING_DATETIME'] = pd.to_datetime(load['READING_DATETIME'])
    load['READING_DATETIME'] = load['READING_DATETIME'] - timedelta(seconds=1)
    load['READING_DATETIME'] = load['READING_DATETIME'].astype(str)
    load = load.groupby([load['READING_DATETIME'].str[:10]]).sum()
    load.index.name = 'READING_DATETIME'
    load = load.reset_index()
    load['mean'] = [np.nanmean(row[1:], dtype=float) for row in load.values]
    load = load.loc[:, ("READING_DATETIME", 'mean')]
    return jsonify({'Time': list(load.READING_DATETIME), "Mean": list(load['mean'])})


@app.route('/demo_options/<name>')
def demo_options(name):
    load_2_demo_map = pd.read_csv('data/load_2_demo_map.csv')
    demo_file_name = load_2_demo_map[load_2_demo_map['load'] == name]['demo'].iloc[0]
    demo_config_file_name = load_2_demo_map[load_2_demo_map['load'] == name]['demo_config'].iloc[0]
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

    x=1
    return jsonify({'actual_names': actual_names, "display_names": display_names_dict, "options": options})


if __name__ == '__main__':
    app.run(debug=True)

    #init_gui(app, width=1200, height=800, window_title='TDA')  # This one runs it as a standalone app