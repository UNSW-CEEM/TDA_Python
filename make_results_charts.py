import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from time import time


def _bill_distribution(results, name):
    chart = go.Histogram(x=results['Bill'], histnorm='probability', name=name)
    return chart


_single_variable_chart_methods = {'Bill Distribution': _bill_distribution}


def singe_variable_chart(chart_name, results_by_case):
    chart_data = []
    for case_name, results in results_by_case.items():
        chart_data.append(_single_variable_chart_methods[chart_name](results, case_name))
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data


def dual_variable_chart_method(data, x_axis, y_axis, name):
    chart = go.Scattergl(x=data[x_axis], y=data[y_axis], mode='markers', name=name)
    return chart


def dual_variable_chart(results_by_case, x_axis, y_axis):
    chart_data = []
    for case_name, results in results_by_case.items():
        chart_data.append(dual_variable_chart_method(results, x_axis, y_axis, case_name))
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data


def is_component(suffixes, name_to_check):
    for suffix in suffixes:
        if suffix in name_to_check:
            return True
    return False


def bill_components(data):
    data = data.sort_values('Bill', ascending=False)
    data = data.reset_index(drop=True)
    traces = []
    compenent_suffixes = ['Retailer', 'DUOS', 'NUOS', 'TUOS', 'DTOUS']
    potential_components = [col for col in data.columns if is_component(compenent_suffixes, col)]
    for component in potential_components:
        trace = dict(name=component,
                     x=data.index.values,
                     y=data[component],
                     mode='lines',
                     stackgroup='one')
        traces.append(trace)
    return traces


single_case_chart_methods = {'bill_components': bill_components}


def single_case_chart(chart_name, results_to_plot):
    chart_data = single_case_chart_methods[chart_name](results_to_plot)
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data
