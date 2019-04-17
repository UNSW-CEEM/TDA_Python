import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from time import time


def get_average_annual_profile(load, series_name=''):
    t0 = time()
    load = load.groupby('READING_DATETIME', as_index=False)['Energy_kWh'].mean()
    load.columns = ['READING_DATETIME', 'mean']
    print('time to find mean {}'.format(time() - t0))
    load = go.Scattergl(x=load['READING_DATETIME'], y=load['mean'], name=series_name)
    return load


chart_methods = {'Annual Average Profile': get_average_annual_profile}
