import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from time import time
from datetime import datetime, timedelta


def get_average_annual_profile(load, load_filtered, series_name):
    Xaxis = "Time"
    Yaxis = "Average Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)
    
    if len(series_name) == 1:
        ### load mean
        load2 = load.copy()
        load2.set_index('Datetime',inplace=True)
        
        load_mean = load2.mean(axis=1)

        trace1 = go.Scattergl(x=load_mean.index, y=load_mean.values, name=series_name[0])

        ### no load_filtered data

        data = {'data':[trace1],'layout':layout}
        return data
    else:    
        if load_filtered.shape[1] <= 1:

            data = {'data':[],'layout':layout}
            return data

        else:
            ### load mean
            load2 = load.copy()
            load2.set_index('Datetime',inplace=True)
            
            load_mean = load2.mean(axis=1)

            trace1 = go.Scattergl(x=load_mean.index, y=load_mean.values, name=series_name[0])


            ### load_filtered mean
            load_filtered2 = load_filtered.copy()
            load_filtered2.set_index('Datetime',inplace=True)

            load_filtered_mean = load_filtered2.mean(axis=1)

            trace2 = go.Scattergl(x=load_filtered_mean.index, y=load_filtered_mean.values, name=series_name[1])

            data = {'data':[trace1, trace2],'layout':layout}
            return data


def get_daily_kWh_hist(load, load_filtered, series_name):

    Xaxis = "Daily Electricity (kWh)"
    Yaxis = "Percentage"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)
    
    if len(series_name)==1:

        load2 = load.copy()
        del load2['Datetime']
        load_sum = load2.sum(axis=0)/2/365

        # no filtered data

        trace1 = go.Histogram(x=list(load_sum),histnorm='probability',name=series_name[0], xbins=dict(
        start=min(load_sum),
        end=max(load_sum),
        size=(max(load_sum)-min(load_sum))/50))

        data ={'data': [trace1], 'layout':layout}
        return data
    else:
        if load_filtered.shape[1] <= 1:
            data ={'data': [], 'layout':layout}
            return data
        else:
            load2 = load.copy()
            del load2['Datetime']
            load_sum = load2.sum(axis=0)/2/365

            load_filtered2 = load_filtered.copy()
            del load_filtered2['Datetime']
            load_filtered_sum = load_filtered2.sum(axis=0)/2/365

            trace1 = go.Histogram(x=list(load_sum),histnorm='probability',name=series_name[0])
            trace2 = go.Histogram(x=list(load_filtered_sum),histnorm='probability',name=series_name[1])

            data ={'data': [trace1, trace2], 'layout':layout}
            #data = trace
            return data

def get_daily_average_profile(x):
    x_array = np.array(x).reshape((-1,48))
    return np.nanmean(x_array,axis=0)


def get_daily_profiles(load):

    Xaxis = "Time"
    Yaxis = "Average Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12),
                       tickmode = 'array',
                       tickvals = [2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46],
                       ticktext = ['01:00', '03:00', '05:00', '07:00', '09:00', '11:00','13:00','15:00','17:00','19:00','21:00','23:00']),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)

    if load.shape[1] <= 1:
        data ={'data': [], 'layout':layout}
        return data
    else:
        load2=load.copy()
        del load2['Datetime']

        load_daily_average = load2.apply(get_daily_average_profile)


        trace_list = []
        for i in range(load_daily_average.shape[1]):
            trace = go.Scatter(x=list(range(0,48)), y=list(load_daily_average.iloc[:,i]), name = load_daily_average.columns[i])
            trace_list.append(trace)
        
        data ={'data': trace_list, 'layout':layout}

        return data

def get_daily_profile_interquartile(load):

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12),
                       tickmode = 'array',
                       tickvals = [2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46],
                       ticktext = ['01:00', '03:00', '05:00', '07:00', '09:00', '11:00','13:00','15:00','17:00','19:00','21:00','23:00']),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)

    if load.shape[1] <= 1:
        data ={'data': [], 'layout':layout}
        return data
    else:
        load2=load.copy()
        del load2['Datetime']

        load_daily_average = load2.apply(get_daily_average_profile)

        qr1 = np.nanpercentile(np.array(load_daily_average), 75, interpolation='midpoint',axis=1)
        qr2 = np.nanpercentile(np.array(load_daily_average), 50, interpolation='midpoint',axis=1)
        qr3 = np.nanpercentile(np.array(load_daily_average), 25, interpolation='midpoint',axis=1)

        trace1 = go.Scatter(x=list(range(0,48)),y=list(qr3),fill=None, name = '25%')
        trace2 = go.Scatter(x=list(range(0,48)),y=list(qr2),fill='tonexty', name = '50%')
        trace3 = go.Scatter(x=list(range(0,48)),y=list(qr1),fill='tonexty', name = '75%')

        data ={'data': [trace1, trace2, trace3], 'layout':layout}

        return data

def get_average_load_duration_curve(load):

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=False)

    if load.shape[1] <= 1:
        data = {'data': [], 'layout':layout}
        return data

    else:
        load2=load.copy()
        load2.drop(['Datetime'], axis=1, inplace=True)
        
        load_average = load2.mean(axis=1)
        load_average_sort = load_average.sort_values(ascending = False, inplace = False, na_position ='last')

        trace = go.Scatter(x=list(range(0,17520)),y=list(load_average_sort))
        data = {'data': [trace], 'layout':layout}
        return data

def get_average_peak_day_profile(load):

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=False)

    if load.shape[1] <= 1:
        data = {'data': [], 'layout':layout}
        return data
    else:
        load2=load.copy()
        load2.set_index('Datetime',inplace=True)
            
        load_average = load2.mean(axis=1)

        # organise data
        load_average = pd.DataFrame(load_average)
        load_average.columns = ['power']

        # find the max day
        peak_day_index = load_average['power'].idxmax()

        peak_day = pd.to_datetime(peak_day_index, format='%Y-%m-%d')

        peak_day_string = peak_day.strftime("%Y-%m-%d")

        # filter for the peak day
        load_average_peak_day = load_average.loc[peak_day_string]
        trace = go.Scatter(x=load_average_peak_day.index,y=list(load_average_peak_day['power']))

        data = {'data': [trace], 'layout':layout}
        return data

def get_monthly_average_kWh(load):

    Xaxis = "Daily Electricity (kWh)"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=False)

    if load.shape[1] <= 1:
        data = {'data': [], 'layout':layout}
        return data
    else:

        load2=load.copy()
        load2.set_index('Datetime',inplace=True)
            
        load_average = load2.mean(axis=1)

        # find mean for each month
        monthly_mean = load_average.resample('M').mean()

        monthly_mean = monthly_mean*24
        
        month_name = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

        trace = go.Bar(x=month_name,y=monthly_mean.values)

        data = {'data': [trace], 'layout':layout}

        return data

def get_seasonal_daily_pattern(load):

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12),
                       tickmode = 'array',
                       tickvals = [2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46],
                       ticktext = ['01:00', '03:00', '05:00', '07:00', '09:00', '11:00','13:00','15:00','17:00','19:00','21:00','23:00']),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)

    if load.shape[1] <= 1:
        data = {'data': [], 'layout':layout}
        return data
    else:
        load2=load.copy()
        load2.set_index('Datetime',inplace=True)
            
        load_average = load2.mean(axis=1)

        # organise data
        load_average = pd.DataFrame(load_average)
        load_average.columns = ['power']
        load_average['Date'] = load_average.index

        load_average['Month_Number'] = load_average['Date'].dt.month

        # summer
        #load_summer = load_average[load_average['Month_Number'] == 1 or load_average['Month_Number'] == 11 or load_average['Month_Number'] == 12]
        load_summer = load_average[load_average['Month_Number'].isin([1,11,12])]
        load_summer_reshape = np.array(load_summer['power']).reshape(-1,48)
        load_summer_daily = np.nanmean(load_summer_reshape,axis=0)
        trace1 = go.Scatter(x=list(range(0,48)), y=load_summer_daily, name= 'Summer', mode='lines')

        # winter
        load_winter = load_average[load_average['Month_Number'].isin([6,7,8])]
        load_winter_reshape = np.array(load_winter['power']).reshape(-1,48)
        load_winter_daily = np.nanmean(load_winter_reshape,axis=0)
        trace2 = go.Scatter(x=list(range(0,48)), y=load_winter_daily, name= 'Winter', mode='lines')

        data = {'data': [trace1, trace2], 'layout':layout}
        return data

chart_methods = {'Annual Average Profile': get_average_annual_profile,
                 'Daily kWh Histogram':get_daily_kWh_hist,
                 'Daily Profiles':get_daily_profiles,
                 'Daily Profile Interquartile Range':get_daily_profile_interquartile,
                 'Average Load Duration Curve':get_average_load_duration_curve,
                 'Average Peak Day Profile':get_average_peak_day_profile,
                 'Monthly Average kWh':get_monthly_average_kWh,
                 'Seasonal Daily Pattern':get_seasonal_daily_pattern}
