import plotly.graph_objs as go
import json
import plotly


def annual_profile(price):
    price = go.Scattergl(x=price['SETTLEMENTDATE'], y=price['RRP'])
    chart_data = json.dumps([price], cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data