import pandas as pd


def plot_ly_to_pandas(plot_ly_format_data):
    series_list = []
    titles = {}
    if 'x_title' in plot_ly_format_data.keys():
        titles['x'] = plot_ly_format_data['x_title']
        titles['y'] = plot_ly_format_data['y_title']
    columns = []
    for series in plot_ly_format_data['chart_data']:
        series_dataframe = pd.DataFrame()
        for axis in ['x', 'y', 'labels', 'values']:
            if axis in series.keys():
                if axis in titles.keys():
                    title = titles[axis]
                else:
                    title = axis
                series_dataframe[title] = series[axis]
                if title not in columns:
                    columns.append(title)
        if 'name' in series.keys():
            series_dataframe['Series'] = series['name']
            if 'Series' not in columns:
                columns.insert(0, 'Series')
        series_list.append(series_dataframe)
    export_dataframe = pd.concat(series_list, ignore_index=True)
    export_dataframe = export_dataframe.loc[:, columns]
    return export_dataframe
