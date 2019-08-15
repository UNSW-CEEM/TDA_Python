def get_unique_default_case_name(names_in_use):
    base_name = "Case "
    not_unique = True
    number = 1
    while not_unique:
        test_name = base_name + str(number)
        if test_name not in names_in_use:
            break
        number += 1
    return test_name


def get_demographic_options_from_demo_file(demo_file):
    n = len(demo_file.columns) if len(demo_file.columns) < 11 else 11
    actual_names = list(demo_file.columns[1:n])
    display_names = list(demo_file.columns[1:n])
    options = {}
    display_names_dict = {}
    for name, display_name in zip(actual_names, display_names):
        options[name] = ['All'] + list([str(val) for val in demo_file[name].unique()])
        display_names_dict[name] = display_name
    return {'actual_names': actual_names, "display_names": display_names_dict, "options": options}


def filter_load_data(raw_data, demo_info, filter_options):
    filtered = False

    for column_name, selected_options in filter_options.items():
        if 'All' not in selected_options:
            demo_info = demo_info[demo_info[column_name].isin([selected_options])]
            filtered = True

    customer_id = [c_id for c_id in list(demo_info['CUSTOMER_KEY']) if c_id in raw_data.columns]

    filtered_data = raw_data.loc[:, ['Datetime'] + customer_id]

    return filtered, filtered_data


def n_users(load_data):
    n = len(load_data.columns) - 1
    return n
