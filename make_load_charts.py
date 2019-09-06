import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from time import time
from datetime import datetime, timedelta


def get_average_annual_profile(load, load_filtered, series_name):
    # print(load.head())
    t0 = time()

    ### load mean
    load2 = load.copy()
    load2.set_index('Datetime',inplace=True)
    
    # print(load2.head())
    load_mean = load2.mean(axis=1)
    # print(load_mean.head())

    trace1 = go.Scattergl(x=load_mean.index, y=load_mean.values, name=series_name[0])


    ### load_filtered mean
    # print('=================== filtered')
    # print(load_filtered.head())
    load_filtered2 = load_filtered.copy()
    load_filtered2.set_index('Datetime',inplace=True)

    # print(load_filtered2.head())
    load_filtered_mean = load_filtered2.mean(axis=1)
    # print(load_filtered_mean.head())

    trace2 = go.Scattergl(x=load_filtered_mean.index, y=load_filtered_mean.values, name=series_name[1])


    Xaxis = "Time"
    Yaxis = "Average Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

    data = {'data':[trace1, trace2],'layout':layout}
    return data


def get_daily_kWh_hist(load, load_filtered, series_name):
    # print(load.head())
    load2 = load.copy()
    del load2['Datetime']
    load_sum = load2.sum(axis=0)/2/365
    # print(load2.head())

    # print(load_filtered.head())
    load_filtered2 = load_filtered.copy()
    del load_filtered2['Datetime']
    load_filtered_sum = load_filtered2.sum(axis=0)/2/365
    # print(load_filtered2.head())


    trace1 = go.Histogram(x=list(load_sum),histnorm='probability',name=series_name[0])
    trace2 = go.Histogram(x=list(load_filtered_sum),histnorm='probability',name=series_name[1])

    Xaxis = "Daily Electricity (kWh)"
    Yaxis = "Percentage"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

    data ={'data': [trace1, trace2], 'layout':layout}
    #data = trace
    return data

def get_daily_average_profile(x):
    x_array = np.array(x).reshape((-1,48))
    return np.nanmean(x_array,axis=0)


def get_daily_profiles(load):
    load2=load.copy()
    # print(load2.head())
    del load2['Datetime']
    # print(load2.head())

    load_daily_average = load2.apply(get_daily_average_profile)
    # print(load_daily_average.head())
    # print(load_daily_average.shape)


    trace_list = []
    for i in range(load_daily_average.shape[1]):
        trace = go.Scatter(x=list(range(0,48)), y=list(load_daily_average.iloc[:,i]), name = load_daily_average.columns[i])
        trace_list.append(trace)
    
    Xaxis = "Time"
    Yaxis = "Average Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

    data ={'data': trace_list, 'layout':layout}

    return data

def get_daily_profile_interquartile(load):
    load2=load.copy()
    # print(load2.head())
    del load2['Datetime']
    # print(load2.head())

    load_daily_average = load2.apply(get_daily_average_profile)
    # print(load_daily_average.head())
    # print(load_daily_average.shape)

    # print(np.array(load_daily_average))

    qr1 = np.nanpercentile(np.array(load_daily_average), 75, interpolation='midpoint',axis=1)
    qr2 = np.nanpercentile(np.array(load_daily_average), 50, interpolation='midpoint',axis=1)
    qr3 = np.nanpercentile(np.array(load_daily_average), 25, interpolation='midpoint',axis=1)

    # print(qr1)
    # print(qr2)
    # print(qr3)

    trace1 = go.Scatter(x=list(range(0,48)),y=list(qr3),fill=None, name = '25%')
    trace2 = go.Scatter(x=list(range(0,48)),y=list(qr2),fill='tonexty', name = '50%')
    trace3 = go.Scatter(x=list(range(0,48)),y=list(qr1),fill='tonexty', name = '75%')

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

    data ={'data': [trace1, trace2, trace3], 'layout':layout}

    return data

def get_average_load_duration_curve(load):
    load2=load.copy()
    load2.drop(['Datetime'], axis=1, inplace=True)
    
    load_average = load2.mean(axis=1)
    # print(load_average.head())

    load_average_sort = load_average.sort_values(ascending = False, inplace = False, na_position ='last')
    # print(load_average_sort)

    trace = go.Scatter(x=list(range(0,17520)),y=list(load_average_sort))

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

    data = {'data': [trace], 'layout':layout}
    return data

def get_average_peak_day_profile(load):

    load2=load.copy()
    load2.set_index('Datetime',inplace=True)
        
    load_average = load2.mean(axis=1)
    # print(load_average.head())

    # organise data
    load_average = pd.DataFrame(load_average)
    load_average.columns = ['power']

    # find the max day
    peak_day_index = load_average['power'].idxmax()
    # print('peak_day_index')
    # print(peak_day_index)
    # print(type(peak_day_index))

    peak_day = pd.to_datetime(peak_day_index, format='%Y-%m-%d')
    # print(peak_day)

    peak_day_string = peak_day.strftime("%Y-%m-%d")

    # filter for the peak day
    load_average_peak_day = load_average.loc[peak_day_string]
    # print(load_average_peak_day)

    trace = go.Scatter(x=load_average_peak_day.index,y=list(load_average_peak_day['power']))

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

    data = {'data': [trace], 'layout':layout}
    return data

def get_monthly_average_kWh(load):

    load2=load.copy()
    load2.set_index('Datetime',inplace=True)
        
    load_average = load2.mean(axis=1)
    # print(load_average.head())

    # find mean for each month
    monthly_mean = load_average.resample('M').mean()
    # print(monthly_mean)

    monthly_mean = monthly_mean*24
    # print(list(monthly_mean.values))

    trace = go.Bar(x=list(range(0,12)),y=monthly_mean.values)

    Xaxis = "Daily Electricity (kWh)"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

    data = {'data': [trace], 'layout':layout}

    return data

def get_seasonal_daily_pattern(load):

    load2=load.copy()
    load2.set_index('Datetime',inplace=True)
        
    load_average = load2.mean(axis=1)
    # print(load_average.head())

    # organise data
    load_average = pd.DataFrame(load_average)
    load_average.columns = ['power']
    load_average['Date'] = load_average.index
    # print(load_average.head())

    load_average['Month_Number'] = load_average['Date'].dt.month
    # print(load_average.head())

    # summer
    #load_summer = load_average[load_average['Month_Number'] == 1 or load_average['Month_Number'] == 11 or load_average['Month_Number'] == 12]
    load_summer = load_average[load_average['Month_Number'].isin([1,11,12])]
    # print(load_summer.head())
    load_summer_reshape = np.array(load_summer['power']).reshape(-1,48)
    load_summer_daily = np.nanmean(load_summer_reshape,axis=0)
    trace1 = go.Scatter(x=list(np.array(range(0,48))/2), y=load_summer_daily, name= 'Summer', mode='lines')

    # winter
    load_winter = load_average[load_average['Month_Number'].isin([6,7,8])]
    load_winter_reshape = np.array(load_winter['power']).reshape(-1,48)
    load_winter_daily = np.nanmean(load_winter_reshape,axis=0)
    trace2 = go.Scatter(x=list(np.array(range(0,48))/2), y=load_winter_daily, name= 'Winter', mode='lines')

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

    data = {'data': [trace1, trace2], 'layout': layout}

    return data

chart_methods = {'Annual Average Profile': get_average_annual_profile,
                 'Daily kWh Histogram':get_daily_kWh_hist,
                 'Daily Profiles':get_daily_profiles,
                 'Daily Profile Interquartile Range':get_daily_profile_interquartile,
                 'Average Load Duration Curve':get_average_load_duration_curve,
                 'Average Peak Day Profile':get_average_peak_day_profile,
                 'Monthly Average kWh':get_monthly_average_kWh,
                 'Seasonal Daily Pattern':get_seasonal_daily_pattern}
