import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from time import time


def bill_distribution(results):
    chart = [go.Histogram(x=results['Bill'], histnorm='probability')]
    return chart


results_chart_methods = {'Bill Distribution': bill_distribution}