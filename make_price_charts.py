import plotly.graph_objs as go
import json
import plotly


def get_default_layout():
    layout = go.Layout(xaxis=dict(title='', title_font=dict(size=12), tickfont=dict(size=12)),
                       yaxis=dict(title='', title_font=dict(size=12), tickfont=dict(size=12),
                                  tickformat=',.2f'),
                       margin=dict(l=80, r=35, b=40, t=20, pad=0),
                       paper_bgcolor='#EEEEEE',
                       plot_bgcolor='#c7c7c7',
                       showlegend=True)
    return layout


def annual_profile(price):
    price = go.Scattergl(x=price['SETTLEMENTDATE'], y=price['RRP'])
    annual_profile_layout = get_default_layout()
    annual_profile_layout['xaxis']['title'] = 'Time'
    annual_profile_layout['yaxis']['title'] = 'Price ($/MWh)'
    chart_data = {'data': [price], 'layout': annual_profile_layout}
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data


def price_duration_curve(price):
    price = price.sort_values('RRP', ascending=False)
    price = price.reset_index(drop=True)
    price['duration'] = price.index
    price['duration'] = (price['duration'] / price['duration'].max()) * 100
    chart_data = go.Scattergl(x=price['duration'], y=price['RRP'])
    annual_profile_layout = get_default_layout()
    annual_profile_layout['xaxis']['title'] = 'Duration (%)'
    annual_profile_layout['yaxis']['title'] = 'Price ($/MWh)'
    annual_profile_layout['yaxis']['tickvals'] = [1, 10, 100, 1000, price['RRP'].max()]
    annual_profile_layout['yaxis']['type'] = 'log'
    chart_data = {'data': [chart_data], 'layout': annual_profile_layout}
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data


price_chart_methods = {'Annual Profile': annual_profile, 'Price Duration Curve': price_duration_curve}


def get_price_chart(price, chart_type):
    return price_chart_methods[chart_type](price)
