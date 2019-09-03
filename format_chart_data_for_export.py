import pandas as pd


def plot_ly_to_pandas(plot_ly_format_data):
    series_list = []
    x_title = plot_ly_format_data['x_title']
    y_title = plot_ly_format_data['y_title']
    for series in plot_ly_format_data['chart_data']:
        series_dataframe = pd.DataFrame()
        series_dataframe[x_title] = series['x']
        series_dataframe[y_title] = series['y']
        if 'name' in series.keys():
            series_dataframe['Series'] = series['name']
        series_list.append(series_dataframe)
    export_dataframe = pd.concat(series_list, ignore_index=True)
    if 'Series' in export_dataframe.columns:
        export_dataframe = export_dataframe.loc[:, ['Series', x_title, y_title]]
    return export_dataframe
