from flask import Flask, render_template, request, jsonify
import os
from pyfladesk import init_gui
import sys
import pandas as pd


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
    load = pd.read_csv('data/'+name)
    load['mean'] = load.mean(axis=1)
    load = load.loc[:, ("READING_DATETIME", 'mean')]
    return jsonify({'Time': list(load.READING_DATETIME), "Mean": list(load['mean'])})


if __name__ == '__main__':
    app.run(debug=True)

    #init_gui(app, width=1200, height=800, window_title='TDA')  # This one runs it as a standalone app