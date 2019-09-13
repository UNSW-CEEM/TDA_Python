import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from time import time


def _bill_distribution(load_and_results_by_case):

    results_by_case = load_and_results_by_case['results']

    Xaxis = "Bill (AUD)"
    Yaxis = "Percentage"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)

    trace = []
    for case_name, results in results_by_case.items():
        trace.append(go.Histogram(x=results['Bill'], histnorm='probability', name=case_name))

    return {'data': trace, 'layout':layout}

def _bill_box_plot(load_and_results_by_case):

    results_by_case = load_and_results_by_case['results']

    Xaxis = "Case"
    Yaxis = "Bill (AUD)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)

    trace = []
    for case_name, results in results_by_case.items():
        trace.append(go.Box(y=results['Bill'], name=case_name))

    return {'data': trace, 'layout':layout}

def _average_annual_profile(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']

    Xaxis = "Time"
    Yaxis = "Average Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)

    trace = []
    for case_name, load in load_by_case.items():
        load2 = load.copy()
        load_mean = load.mean(axis=1)
        trace.append(go.Scattergl(x=load_mean.index, y=load_mean.values, name=case_name))

    return {'data': trace, 'layout':layout}

def _daily_kWh_histogram(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']

    Xaxis = "Daily Electricity (kWh)"
    Yaxis = "Percentage"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                    yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                    showlegend=True)
    
    trace = []
    for case_name, load in load_by_case.items():
        load2 = load.copy()
        load_sum = load2.sum(axis=0)/2/365
        trace.append(go.Histogram(x=list(load_sum),histnorm='probability',name=case_name,xbins=dict(
        start=min(load_sum),
        end=max(load_sum),
        size=(max(load_sum)-min(load_sum))/50)))
    
    return {'data': trace, 'layout':layout}

def _average_load_duration_curve(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']

    Xaxis = "Time"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)
    
    trace = []
    for case_name, load in load_by_case.items():

        load2 = load.copy()
        load_average = load2.mean(axis=1)
        load_average_sort = load_average.sort_values(ascending = False, inplace = False, na_position ='last')
        load_average_sort = load_average_sort.reset_index(drop = True) 

        trace.append(go.Scatter(x=load_average_sort.index,y=load_average_sort.values, name=case_name))

    return {'data': trace, 'layout':layout}


def _monthly_average_kWh(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']

    Xaxis = "Daily Electricity (kWh)"
    Yaxis = "Load (kW)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)
    
    trace = []
    for case_name, load in load_by_case.items():
        load2 = load.copy()
        load_average = load2.mean(axis=1)

        # find mean for each month
        monthly_mean = load_average.resample('M').mean()
        monthly_mean = monthly_mean*24
        month_name = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

        trace.append(go.Bar(x=month_name,y=monthly_mean.values, name=case_name))

    return {'data': trace, 'layout':layout}


def _seasonal_daily_pattern(load_and_results_by_case):

    load_by_case = load_and_results_by_case['load']

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

        load2 = load.copy()
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

    return {'data': trace, 'layout':layout}

def _monthly_peak_time(load_and_results_by_case):
    load_by_case = load_and_results_by_case['load']

    Xaxis = "Month"
    Yaxis = "Time of day (Hour)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)
    
    trace = []
    for case_name, load in load_by_case.items():
        load2 = load.copy()
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

    return {'data': trace, 'layout':layout}


########################### charts dict: _single_variable_chart_methods

_single_variable_chart_methods = {'Bill Distribution': _bill_distribution,
                                  'Bill Box Plot': _bill_box_plot,
                                  'Average Annual Profile': _average_annual_profile,
                                  'Daily kWh Histogram':_daily_kWh_histogram,
                                  'Average Load Duration Curve':_average_load_duration_curve,
                                  'Monthly Average kWh':_monthly_average_kWh,
                                  'Seasonal Daily Pattern':_seasonal_daily_pattern,
                                  'Monthly Peak Time':_monthly_peak_time}



def singe_variable_chart(chart_name, load_and_results_by_case):
    chart_data = _single_variable_chart_methods[chart_name](load_and_results_by_case)
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data

#################################################################################################
# dual variable

def _get_annual_kWh(results, load, network_load, details, axis):
    axis_name = "Annual kWh"
    axis_data = results['Annual_kWh']
    return {'axis_name':axis_name, 'axis_data':axis_data}


def _get_avg_demand_n_peaks(results, load, network_load, details, axis):

    if axis == 'x_axis':
        N_peaks = int(details['x_axis_n_peaks'])
        one_peak_per_day_status = details['x_axis_one_peak_per_day']
    if axis == 'y_axis':
        N_peaks = int(details['y_axis_n_peaks'])
        one_peak_per_day_status = details['y_axis_one_peak_per_day']

    axis_name = "Average Demand at " + str(N_peaks) + " Network Peaks"
    
    network_load2 = network_load.copy()
    network_load2['Month_Number'] = network_load2.index.month

    network_load_filtered = network_load2.copy()

    if details['include_spring'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([3,4,5])]
    if details['include_summer'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([6,7,8])]
    if details['include_autumn'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([9,10,11])]
    if details['include_winter'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([1,2,12])]
    
    del network_load_filtered['Month_Number']


    if one_peak_per_day_status == False:

        network_load_filtered2=network_load_filtered.copy()
            
        network_load_average = network_load_filtered2.mean(axis=1)
        network_load_average_sort = network_load_average.sort_values(ascending = False, inplace = False, na_position ='last')

        selected_datetime = network_load_average_sort.index[0:N_peaks]

        load2 = load.copy()

        selected_load = load2.loc[selected_datetime]

        selected_load_average = selected_load.mean(axis=0)

        axis_data = list(selected_load_average)

        return {'axis_name':axis_name, 'axis_data':axis_data}
        
    else:
        network_load_filtered2=network_load_filtered.copy()
            
        network_load_average = network_load_filtered2.mean(axis=1)

        # find peak for each day
        network_daily_peak = network_load_average.resample('D').max()

        network_daily_peak_sort = network_daily_peak.sort_values(ascending = False, inplace = False, na_position ='last')

        selected_datetime = network_daily_peak_sort.index[0:N_peaks]

        load2 = load.copy()

        load_daily_peak = load2.resample('D').max()

        selected_load = load_daily_peak.loc[selected_datetime]

        selected_load_average = selected_load.mean(axis=0)
        axis_data = list(selected_load_average)
        return {'axis_name':axis_name, 'axis_data':axis_data}    



def _get_avg_demand_n_monthly_peaks(results, load, network_load, details, axis):

    if axis == 'x_axis':
        N_peaks = int(details['x_axis_n_peaks'])
        one_peak_per_day_status = details['x_axis_one_peak_per_day']
    if axis == 'y_axis':
        N_peaks = int(details['y_axis_n_peaks'])
        one_peak_per_day_status = details['y_axis_one_peak_per_day']

    axis_name = "Average Demand at " + str(N_peaks) + " Network Peaks"
    
    network_load2 = network_load.copy()
    network_load2['Month_Number'] = network_load2.index.month
    network_load_filtered = network_load2.copy()

    if details['include_spring'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([3,4,5])]
    if details['include_summer'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([6,7,8])]
    if details['include_autumn'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([9,10,11])]
    if details['include_winter'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([1,2,12])]

    network_load_filtered_by_month = []
    for i in range(12):
        monthly_data = network_load_filtered[network_load_filtered['Month_Number'].isin([i+1])]
        del monthly_data['Month_Number']
        network_load_filtered_by_month.append(monthly_data)

    if one_peak_per_day_status == False:

        selected_datetime = []
        for i in range(12):
            network_load_filtered_by_month_i=network_load_filtered_by_month[i].copy()
                
            network_load_average = network_load_filtered_by_month_i.mean(axis=1)
            network_load_average_sort = network_load_average.sort_values(ascending = False, inplace = False, na_position ='last')

            selected_datetime = selected_datetime + list(network_load_average_sort.index[0:N_peaks])

        load2 = load.copy()

        selected_load = load2.loc[selected_datetime]

        selected_load_average = selected_load.mean(axis=0)

        axis_data = list(selected_load_average)

        return {'axis_name':axis_name, 'axis_data':axis_data}
    else:

        selected_datetime = []
        for i in range(12):
            network_load_filtered_by_month_i=network_load_filtered_by_month[i].copy()
                
            network_load_average = network_load_filtered_by_month_i.mean(axis=1)

            network_daily_peak = network_load_average.resample('D').max()

            network_daily_peak_sort = network_daily_peak.sort_values(ascending = False, inplace = False, na_position ='last')

            selected_datetime = selected_datetime + list(network_daily_peak_sort.index[0:N_peaks])

        load2 = load.copy()

        load_daily_peak = load2.resample('D').max()

        selected_load = load_daily_peak.loc[selected_datetime]

        selected_load_average = selected_load.mean(axis=0)
        axis_data = list(selected_load_average)
        return {'axis_name':axis_name, 'axis_data':axis_data}    


def _get_avg_demand_top_n_peaks(results, load, network_load, details, axis):

    if axis == 'x_axis':
        N_peaks = int(details['x_axis_n_peaks'])
        one_peak_per_day_status = details['x_axis_one_peak_per_day']
    if axis == 'y_axis':
        N_peaks = int(details['y_axis_n_peaks'])
        one_peak_per_day_status = details['y_axis_one_peak_per_day']

    axis_name = "Average Demand at " + str(N_peaks) + " Network Peaks"
    
    load2 = load.copy()
    load2['Month_Number'] = load2.index.month

    load_filtered = load2.copy()

    if details['include_spring'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([3,4,5])]
    if details['include_summer'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([6,7,8])]
    if details['include_autumn'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([9,10,11])]
    if details['include_winter'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([1,2,12])]
    
    del load_filtered['Month_Number']
    

    if one_peak_per_day_status == False:

        load_filtered2=load_filtered.copy()

        load_filtered_sort = pd.concat([load_filtered2[col].sort_values(ascending = False, inplace = False, na_position ='last').reset_index(drop=True) for col in load_filtered2], axis=1, ignore_index=True)

        selected_load = load_filtered_sort.iloc[0:N_peaks,:]

        selected_load_average = selected_load.mean(axis=0)

        axis_data = list(selected_load_average)
        return {'axis_name':axis_name, 'axis_data':axis_data}

    else:

        load_filtered2=load_filtered.copy()

        # find peak for each day
        load_filtered_daily_peak = load_filtered2.resample('D').max()

        load_filtered_daily_peak_sort = pd.concat([load_filtered_daily_peak[col].sort_values(ascending = False, inplace = False, na_position ='last').reset_index(drop=True) for col in load_filtered_daily_peak], axis=1, ignore_index=True)
        selected_load = load_filtered_daily_peak_sort.iloc[0:N_peaks,:]

        selected_load_average = selected_load.mean(axis=0)

        axis_data = list(selected_load_average)  
        return {'axis_name':axis_name, 'axis_data':axis_data}


def _get_avg_demand_top_n_monthly_peaks(results, load, network_load, details, axis):

    if axis == 'x_axis':
        N_peaks = int(details['x_axis_n_peaks'])
        one_peak_per_day_status = details['x_axis_one_peak_per_day']
    if axis == 'y_axis':
        N_peaks = int(details['y_axis_n_peaks'])
        one_peak_per_day_status = details['y_axis_one_peak_per_day']

    axis_name = "Average Demand at " + str(N_peaks) + " Network Peaks"
    
    load2 = load.copy()
    load2['Month_Number'] = load2.index.month
    load_filtered = load2.copy()

    if details['include_spring'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([3,4,5])]
    if details['include_summer'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([6,7,8])]
    if details['include_autumn'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([9,10,11])]
    if details['include_winter'] == False:
        network_load_filtered = network_load_filtered[~network_load_filtered['Month_Number'].isin([1,2,12])]

    load_filtered_by_month = []
    for i in range(12):
        monthly_data = load_filtered[load_filtered['Month_Number'].isin([i+1])]
        del monthly_data['Month_Number']
        load_filtered_by_month.append(monthly_data)

    if one_peak_per_day_status == False:

        selected_load = []
        for i in range(12):
            load_filtered_by_month_i=load_filtered_by_month[i].copy()

            load_filtered_by_month_i_sort = pd.concat([load_filtered_by_month_i[col].sort_values(ascending = False, inplace = False, na_position ='last').reset_index(drop=True) for col in load_filtered_by_month_i], axis=1, ignore_index=True)
            selected_load_by_month = load_filtered_by_month_i_sort.iloc[0:N_peaks,:]

            selected_load.append(list(selected_load_by_month.mean(axis=0)))

        selected_load_average = np.nanmean(np.array(selected_load),axis=0)

        axis_data = list(selected_load_average)

        return {'axis_name':axis_name, 'axis_data':axis_data}
    else:

        selected_load = []
        for i in range(12):
            load_filtered_by_month_i=load_filtered_by_month[i].copy()

            load_filtered_daily_peak_by_month = load_filtered_by_month_i.resample('D').max()

            load_filtered_daily_peak_by_month_sort = pd.concat([load_filtered_daily_peak_by_month[col].sort_values(ascending = False, inplace = False, na_position ='last').reset_index(drop=True) for col in load_filtered_daily_peak_by_month], axis=1, ignore_index=True)
            selected_load_by_month = load_filtered_daily_peak_by_month_sort.iloc[0:N_peaks,:]

            selected_load.append(list(selected_load_by_month.mean(axis=0)))

        selected_load_average = np.nanmean(np.array(selected_load),axis=0)

        axis_data = list(selected_load_average)

        return {'axis_name':axis_name, 'axis_data':axis_data}


def _get_avg_daily_kWh(results, load, network_load, details, axis):
    axis_name = "Average Daily kWh"
    axis_data = []
    load2 = load.copy()

    axis_data = []
    for i in range(load2.shape[1]):
        load_id_array = np.array(load2.iloc[:,i]).reshape((-1,48))
        load_id_daily_kWh = np.sum(load_id_array,axis=1)
        average_daily = np.nanmean(load_id_daily_kWh)
        axis_data.append(average_daily)

    return {'axis_name':axis_name, 'axis_data':axis_data}

def _get_avg_daily_peak(results, load, network_load, details, axis):
    axis_name = "Average Daily Peaks"
    axis_data = []
    load2 = load.copy()

    axis_data = []
    for i in range(load2.shape[1]):
        load_id_array = np.array(load2.iloc[:,i]).reshape((-1,48))
        load_id_daily_peak = np.max(load_id_array,axis=1)
        average_daily = np.nanmean(load_id_daily_peak)
        axis_data.append(average_daily)

    return {'axis_name':axis_name, 'axis_data':axis_data}


def _get_bill(results, load, network_load, details, axis):
    axis_name = "Bill (AUD)"
    axis_data = results['Bill']
    return {'axis_name':axis_name, 'axis_data':axis_data}


def _get_unitised_bill(results, load, network_load, details, axis):
    axis_name = "Unitised Bill (kW)"
    axis_data = results['Bill']
    return {'axis_name':axis_name, 'axis_data':axis_data}


_dual_variable_axis_methods = {'Annual_kWh': _get_annual_kWh,
                               'avg_demand_n_peaks': _get_avg_demand_n_peaks,
                               'avg_demand_n_monthly_peaks': _get_avg_demand_n_monthly_peaks,
                               'avg_demand_top_n_peaks':_get_avg_demand_top_n_peaks,
                               'avg_demand_top_n_monthly_peaks':_get_avg_demand_top_n_monthly_peaks,
                               'avg_daily_kWh':_get_avg_daily_kWh,
                               'avg_daily_peak':_get_avg_daily_peak,
                               'Bill':_get_bill,
                               'unitised_bill_kW':_get_unitised_bill}

def dual_variable_chart(load_and_results_by_case, details):

    results_by_case = load_and_results_by_case['results']
    load_by_case = load_and_results_by_case['load']
    network_load = load_and_results_by_case['network_load']

    trace = []
    for case_name, results in results_by_case.items():
        x_axis_data = _dual_variable_axis_methods[details['x_axis']](results,load_by_case[case_name],network_load, details, axis = 'x_axis')
        y_axis_data = _dual_variable_axis_methods[details['y_axis']](results,load_by_case[case_name],network_load, details, axis = 'y_axis')
        
        dual_data = go.Scattergl(x=x_axis_data['axis_data'], y=y_axis_data['axis_data'], mode='markers', name=case_name)
        

        trace.append(dual_data)
    
    dual_layout = go.Layout(xaxis=dict(title=x_axis_data['axis_name'],rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                            yaxis=dict(title=y_axis_data['axis_name'],rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))
    
    chart_data = {'data': trace, 'layout':dual_layout}
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data


###################################################################
# Single Case Charts

def is_component(suffixes, name_to_check):
    for suffix in suffixes:
        if suffix in name_to_check:
            return True
    return False


def _get_bill_components(data, load_to_plot):

    Xaxis = "Users (sorted by total bill)"
    Yaxis = "Bill (AUD)"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

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
    return {'data':traces, 'layout': layout}

def _get_bill_components_pie_chart(data, load_by_case):

    Xaxis = ""
    Yaxis = ""
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12)),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)))

    selected_columns = [col for col in data.columns if col.endswith('Charge')]

    selected_data = data[selected_columns]

    percentage = []
    for col in selected_data.columns:
        percentage.append(selected_data[col].sum(axis=0)/data['Bill'].sum(axis=0))

    trace = [go.Pie(labels=selected_columns, values=percentage)]

    return {'data':trace, 'layout': layout}

def get_daily_average_profile(x):
    x_array = np.array(x).reshape((-1,48))
    return np.nanmean(x_array,axis=0)

def _get_daily_profile_interquartile_range(results_to_plot, load_to_plot):
    
    Xaxis = "30 Minutes Interval"
    Yaxis = "kWh"
    layout = go.Layout(xaxis=dict(title=Xaxis,title_font=dict(size=12),tickfont=dict(size=12),
                       tickmode = 'array',
                       tickvals = [2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46],
                       ticktext = ['01:00', '03:00', '05:00', '07:00', '09:00', '11:00','13:00','15:00','17:00','19:00','21:00','23:00']),
                       yaxis=dict(title=Yaxis,rangemode='tozero',title_font=dict(size=12),tickfont=dict(size=12)),
                       showlegend=True)

    load_to_plot2=load_to_plot.copy()

    load_daily_average = load_to_plot2.apply(get_daily_average_profile)

    qr1 = np.nanpercentile(np.array(load_daily_average), 75, interpolation='midpoint',axis=1)
    qr2 = np.nanpercentile(np.array(load_daily_average), 50, interpolation='midpoint',axis=1)
    qr3 = np.nanpercentile(np.array(load_daily_average), 25, interpolation='midpoint',axis=1)

    trace1 = go.Scatter(x=list(range(0,48)),y=list(qr3),fill=None, name = '25%')
    trace2 = go.Scatter(x=list(range(0,48)),y=list(qr2),fill='tonexty', name = '50%')
    trace3 = go.Scatter(x=list(range(0,48)),y=list(qr1),fill='tonexty', name = '75%')

    return {'data': [trace1, trace2, trace3], 'layout':layout}


_single_case_chart_methods = {'bill_components': _get_bill_components,
                              'bill_components_pie_chart': _get_bill_components_pie_chart,
                              'daily_profile_interquartile_range': _get_daily_profile_interquartile_range}


def single_case_chart(chart_name, load_and_results_to_plot):
    results_to_plot = load_and_results_to_plot['results']
    load_to_plot = load_and_results_to_plot['load']

    if results_to_plot is not None:
        chart_data = _single_case_chart_methods[chart_name](results_to_plot, load_to_plot)
    else:
        chart_data = []
    chart_data = json.dumps(chart_data, cls=plotly.utils.PlotlyJSONEncoder)
    return chart_data
