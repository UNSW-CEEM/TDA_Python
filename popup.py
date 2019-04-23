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
import data_interface
import easygui

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
    pop = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    pop = Flask(__name__)


# Here you go to http://127.0.0.1:5000/
@pop.route('/')
def index():
    return render_template('popup.html')