import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from time import time


def bill_distribution(results, name):
    chart = go.Histogram(x=results['Bill'], histnorm='probability', name=name)
    return chart


results_chart_methods = {'Bill Distribution': bill_distribution}


def dual_variable_chart_method(data, x_axis, y_axis, name):
    chart = go.Scattergl(x=data[x_axis], y=data[y_axis], mode='markers', name=name)
    return chart


def bill_components(data):
    data = data.sort_values('Bill', ascending=False)
    data = data.reset_index(drop=True)
    traces = []
    potential_components = {'NUOS_DailyCharge': 'Daily', 'NUOS_EnergyCharge': 'Energy', 'NUOS_TOUCharge': 'TOU'}
    for component, legend_name in potential_components.items():
        if component in data.columns:
            trace = dict(
                name=legend_name,
                x=data.index.values,
                y=data[component],
                mode='lines',
                stackgroup='one'
            )
            traces.append(trace)
    return traces


single_case_chart_methods = {'bill_components': bill_components}