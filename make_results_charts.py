import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from time import time


def _bill_distribution(load_and_results_by_case):

    results_by_case = load_and_results_by_case['results']

    print('===== hist plot')

    Xaxis = "Bill (AUD)"
    Yaxis = "Percentage"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)

    trace = []
    for case_name, results in results_by_case.items():
        print(case_name)
        print(results)
        trace.append(go.Histogram(x=results['Bill'], histnorm='probability', name=case_name))

    data ={'data': trace, 'layout':layout}
    return data

def _bill_box_plot(load_and_results_by_case):

    results_by_case = load_and_results_by_case['results']

    print('==== box plot')

    Xaxis = "Case"
    Yaxis = "Bill (AUD)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)

    trace = []
    for case_name, results in results_by_case.items():
        print(case_name)
        print(results)
        trace.append(go.Box(y=results['Bill'], name=case_name))

    data ={'data': trace, 'layout':layout}
    return data

def _average_annual_profile(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']
    print('===== average annual profile')

    Xaxis = "Time"
    Yaxis = "Average Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)

    trace = []
    for case_name, load in load_by_case.items():
        print(case_name)
        print(load)
        load2 = load.copy()
        load2.set_index('Datetime',inplace=True)
        load_mean = load.mean(axis=1)
        trace.append(go.Scattergl(x=load_mean.index, y=load_mean.values, name=case_name))

    data ={'data': trace, 'layout':layout}
    return data

def _daily_kWh_histogram(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']
    print('===== daily kWh histogram')

    Xaxis = "Daily Electricity (kWh)"
    Yaxis = "Percentage"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)
    
    trace = []
    for case_name, load in load_by_case.items():
        print(case_name)
        print(load)

        load2 = load.copy()
        del load2['Datetime']
        load_sum = load2.sum(axis=0)/2/365

        trace.append(go.Histogram(x=list(load_sum),histnorm='probability',name=case_name,xbins=dict(
        start=min(load_sum),
        end=max(load_sum),
        size=(max(load_sum)-min(load_sum))/50)))

    data ={'data': trace, 'layout':layout}
    return data

def _average_load_duration_curve(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']

    print('===== average load duration curve')

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)
    
    trace = []
    for case_name, load in load_by_case.items():
        print(case_name)
        print(load)

        load2 = load.copy()
        load2.drop(['Datetime'], axis=1, inplace=True)
        load_average = load2.mean(axis=1)
        load_average_sort = load_average.sort_values(ascending = False, inplace = False, na_position ='last')

        trace.append(go.Scatter(x=list(range(0,17520)),y=list(load_average_sort), name=case_name))

    data ={'data': trace, 'layout':layout}
    return data


def _monthly_average_kWh(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']

    print('===== monthly average kWh')

    Xaxis = "Daily Electricity (kWh)"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)
    
    trace = []
    for case_name, load in load_by_case.items():
        print(case_name)
        print(load)
        load2 = load.copy()
        load2.set_index('Datetime',inplace=True)
        load_average = load2.mean(axis=1)

        # find mean for each month
        monthly_mean = load_average.resample('M').mean()
        monthly_mean = monthly_mean*24
        month_name = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

        trace.append(go.Bar(x=month_name,y=monthly_mean.values, name=case_name))

    data ={'data': trace, 'layout':layout}
    return data


def _seasonal_daily_pattern(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']

    print('===== seasonal daily pattern')

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12),
                       tickmode = 'array',
                       tickvals = [2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46],
                       ticktext = ['01:00', '03:00', '05:00', '07:00', '09:00', '11:00','13:00','15:00','17:00','19:00','21:00','23:00']),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)
    
    trace = []
    for case_name, load in load_by_case.items():
        print(case_name)
        print(load)

        load2 = load.copy()
        load2.set_index('Datetime',inplace=True)
        load_average = load2.mean(axis=1)

        # organise data
        load_average = pd.DataFrame(load_average)
        load_average.columns = ['power']
        load_average['Date'] = load_average.index
        load_average['Month_Number'] = load_average['Date'].dt.month

        # summer
        load_summer = load_average[load_average['Month_Number'].isin([1,11,12])]
        load_summer_reshape = np.array(load_summer['power']).reshape(-1,48)
        load_summer_daily = np.nanmean(load_summer_reshape,axis=0)
        trace.append(go.Scatter(x=list(range(0,48)), y=load_summer_daily, name= case_name + ' Summer', mode='lines'))

        # winter
        load_winter = load_average[load_average['Month_Number'].isin([6,7,8])]
        load_winter_reshape = np.array(load_winter['power']).reshape(-1,48)
        load_winter_daily = np.nanmean(load_winter_reshape,axis=0)
        trace.append(go.Scatter(x=list(range(0,48)), y=load_winter_daily, name= case_name + ' Winter', mode='lines'))

    data ={'data': trace, 'layout':layout}
    return data

def _monthly_peak_time(load_and_results_by_case):
    load_by_case = load_and_results_by_case['load']

    print('===== monthly peak time')

    Xaxis = "Month"
    Yaxis = "Time of day (Hour)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)
    
    trace = []
    for case_name, load in load_by_case.items():
        print(case_name)
        print(load)
        load2 = load.copy()
        load2.set_index('Datetime',inplace=True)
        load_average = load2.mean(axis=1)

        # organise data
        load_average = pd.DataFrame(load_average)
        load_average.columns = ['power']
        load_average['Date'] = load_average.index
        load_average['Month_Number'] = load_average['Date'].dt.month
        load_average['Hour_Number'] = load_average['Date'].dt.hour
        load_average['Minute_Number'] = load_average['Date'].dt.minute

        # find the peak time (expressed by hour)
        peak_hour_month = []
        for i in range(12):
            load_by_month = load_average[load_average['Month_Number'].isin([i+1])]
            peak_index = load_by_month['power'].idxmax()
            peak_hour_month.append(load_by_month.loc[peak_index,'Hour_Number'] + load_by_month.loc[peak_index,'Minute_Number']/60)

        month_name = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        trace.append(go.Scatter(x=month_name, y=peak_hour_month, name= case_name, mode='markers', marker=dict(size=20)))       

    data ={'data': trace, 'layout':layout}
    return data


########################### charts dict

_single_variable_chart_methods = {'Bill Distribution': _bill_distribution,
                                  'Bill Box Plot': _bill_box_plot,
                                  'Average Annual Profile': _average_annual_profile,
                                  'Daily kWh Histogram':_daily_kWh_histogram,
                                  'Average Load Duration Curve':_average_load_duration_curve,
                                  'Monthly Average kWh':_monthly_average_kWh,
                                  'Seasonal Daily Pattern':_seasonal_daily_pattern,
                                  'Monthly Peak Time':_monthly_peak_time}



def singe_variable_chart(chart_name, load_and_results_by_case):
    # chart_data = []
    # for case_name, results in results_by_case.items():
    #     print(case_name)
    #     print(results)
    #     chart_data.append(_single_variable_chart_methods[chart_name](results, case_name))
    # chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    # return chart_data

    print('call ============= singe_variable_chart')
    print(chart_name)

    chart_data = _single_variable_chart_methods[chart_name](load_and_results_by_case)
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data




def dual_variable_chart_method(data, x_axis, y_axis, name):
    chart = go.Scattergl(x=data[x_axis], y=data[y_axis], mode='markers', name=name)
    return chart


def dual_variable_chart(load_and_results_by_case, x_axis, y_axis):
    results_by_case = load_and_results_by_case['results']
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
    if results_to_plot is not None:
        chart_data = single_case_chart_methods[chart_name](results_to_plot)
    else:
        chart_data = []
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data
