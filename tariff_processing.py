import copy
from ast import literal_eval


def format_tariff_data_for_display(raw_tariff_json):
    display_format = copy.deepcopy(raw_tariff_json)
    display_format['Parameters'] = {}
    if raw_tariff_json['ProviderType'] == 'Network':
        for parameter_name, parameter in raw_tariff_json['Parameters'].items():
            table_set = _add_tables(parameter)
            display_format['Parameters'][parameter_name] = table_set
    else:
        table_set = _add_tables(raw_tariff_json['Parameters'])
        display_format['Parameters']["Retail"] = table_set
    return display_format


def format_tariff_data_for_storage(display_formatted_tariff):
    storage_format = copy.deepcopy(display_formatted_tariff)

    storage_format['Parameters'] = {}
    if display_formatted_tariff['ProviderType'] == 'Network':
        for parameter_name, parameter in display_formatted_tariff['Parameters'].items():
            table_set = _add_dicts(parameter)
            storage_format['Parameters'][parameter_name] = table_set
    else:
        table_set = _add_dicts(display_formatted_tariff['Parameters']["Retail"])
        storage_format['Parameters'] = table_set
    return storage_format


def get_options_from_tariff_set(tariffs, tariff_filter_state):
    # Define the options to update.
    option_types = {'.select_tariff_state': 'State',
                    '.select_tariff_provider': 'Provider',
                    '.select_tariff_type': 'Type',
                    '.select_tariff': 'Name'}
    options = {'.select_tariff_state': [],
               '.select_tariff_provider': [],
               '.select_tariff_type': [],
               '.select_tariff': []}

    # Look at each tariff build up a set of possible options for each option type.
    for tariff in tariffs:
        # Decide if current tariff meets current filters
        add_tariff_as_option = True
        for option_type, option_name in option_types.items():
            if ((tariff_filter_state[option_type] != 'Any') &
               (tariff_filter_state[option_type] != tariff[option_name])) & (option_name != 'Name'):
                add_tariff_as_option = False
        # If the current tariff meets the all the filters add its properties to the allowed options.
        for option_type, option_name in option_types.items():
            if add_tariff_as_option and tariff[option_name] not in options[option_type]:
                options[option_type].append(tariff[option_name])
    return options


def strip_tariff_to_single_component(tariff, component_name):
    if component_name != "Retail":
        components_to_delete = []
        for parameter_name, parameter in tariff['Parameters'].items():
            if parameter_name != component_name:
                components_to_delete.append(parameter_name)
        for component in components_to_delete:
            tariff['Parameters'].pop(component)
    return tariff


def _add_tables(parameter):
    table_set = {}
    for component_name, component in parameter.items():
        table_data = {'table_rows': []}
        if _contains_sub_dict(component):
            table_data['table_header'] = ['Name']
            for sub_component, sub_details in component.items():
                row = [sub_component]
                table_data = _add_row(sub_details, row, table_data)
        else:
            table_data['table_header'] = []
            row = []
            table_data = _add_row(component, row, table_data)
        table_set[component_name] = table_data
    return table_set


def _add_row(component, initial_row, table_data):
    for column_name, column_value in component.items():
        if column_name not in table_data['table_header']:
            table_data['table_header'].append(str(column_name))
        initial_row.append(str(column_value))
    table_data['table_rows'].append(initial_row)
    return table_data


def _contains_sub_dict(test_dict):
    is_dict = False
    for key, value in test_dict.items():
        if type(value) is dict:
            is_dict = True
    return is_dict


def _add_dicts(parameter):
    dict_set = {}
    for component_name, component in parameter.items():
        dict_set[component_name] = _make_dict(component)
    return dict_set


def _make_dict(component):
    if 'Name' in component['table_header']:
        sub_dict = {}
        for row in component['table_rows']:
            sub_dict[row[0]] = dict(zip(component['table_header'][1:],
                                        [_try_convert_to_object(el) for el in row[1:]]))
    else:
        sub_dict = dict(zip(component['table_header'],
                                            [_try_convert_to_object(el) for el in component['table_rows'][0]]))
    return sub_dict


def _try_convert_to_object(string):
    try:
        obj = literal_eval(string)
    except:
        if string == 'inf':
            obj = float('inf')
        else:
            obj = string
    return obj