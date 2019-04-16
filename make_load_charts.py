import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np


def get_chart(filter_data, raw_data, chart_type):
    data = chart_methods[chart_type](filter_data, raw_data)
    graph_json = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graph_json


def average_daily_chart(filter_data, raw_data):
    filtered = get_average_daily_profile(filter_data)
    raw = get_average_daily_profile(raw_data)
    if 'mean' not in filter_data.columns:
        data = [go.Scattergl(x=raw['READING_DATETIME'], y=raw['mean'], name='All Users')]
    else:
        data = [go.Scattergl(x=raw['READING_DATETIME'], y=raw['mean'], name='All Users'),
                go.Scattergl(x=filtered['READING_DATETIME'], y=filtered['mean'], name='Selected Users')]
    return data


def get_average_daily_profile(load):
    load['READING_DATETIME'] = pd.to_datetime(load['READING_DATETIME'])
    load = load.set_index('READING_DATETIME')
    load['mean'] = load.mean(axis=1)
    load = load.reset_index(drop=False)
    load = load.loc[:, ("READING_DATETIME", 'mean')]
    return load


chart_methods = {'Annual Average Profile': average_daily_chart}
