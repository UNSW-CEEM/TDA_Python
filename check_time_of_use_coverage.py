import datetime


def compile_set_of_overlapping_components_on_yearly_basis(tariff_component):
    overlaps = []
    gaps = []
    for month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
        for week_time in ['Weekday', 'Weekend']:
            for hour in range(0, 24):
                for half_hour in [0, 30]:
                    active_components = _overlapping_components(tariff_component, month, hour, half_hour, week_time)
                    if len(active_components) > 1:
                        message = 'Overlaps on Month: {}, Week time: {}, Half hour ending: {}:{} are'.\
                            format(month, week_time, str(hour).zfill(2), str(half_hour).zfill(2))
                        overlaps.append(', '.join([message] + active_components))
                    elif len(active_components) < 1:
                        message = 'No component for Month: {}, Week time: {}, Half hour ending: {}:{}'.\
                            format(month, week_time, str(hour).zfill(2), str(half_hour).zfill(2))
                        gaps.append(message)
    if len(overlaps) == 0:
        overlaps = ['No overlapping components were found in the tariff.']
    if len(gaps) == 0:
        gaps = ['No gaps in the component time intervals were found.']
    overlaps = '\n'.join(overlaps + gaps)
    return overlaps


def _overlapping_components(tariff_component, month, hour, minute, week_time):
    active_components = []
    for comp_name, comp_time_parameters in tariff_component.items():
        if 'Month' not in comp_time_parameters:
            comp_time_parameters['Month'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        if 'Weekday' not in comp_time_parameters:
            comp_time_parameters['Weekday'] = True
        if 'Weekend' not in comp_time_parameters:
            comp_time_parameters['Weekend'] = True
        comp_time_parameters['Month'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        right_month = month in comp_time_parameters['Month']
        right_week_time = comp_time_parameters[week_time]
        for interval_name, interval in comp_time_parameters['TimeIntervals'].items():
            right_time = _is_right_time(interval, hour, minute)
            if right_month and right_week_time and right_time:
                active_components.append(comp_name + ' ' + interval_name)
    return active_components


def _is_right_time(interval, hour, minute):
    start_time = _interpret_user_time_string(interval[0])
    end_time = _interpret_user_time_string(interval[1])
    now_time = datetime.time(hour=hour, minute=minute)
    if start_time < end_time:
        right_time = start_time < now_time <= end_time
    else:
        right_time = (now_time > start_time) or (now_time <= end_time)
    return right_time


def _interpret_user_time_string(string):
    if string.split(':')[0] == '24':
        string = string.replace('24', '00')
    time_object = datetime.datetime.strptime(string, '%H:%M').time()
    return time_object
