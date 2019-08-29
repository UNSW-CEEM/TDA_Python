import pandas as pd


def process_case(case_name, project_data):
    data_for_export = []
    data_for_export = _add_single_item_with_label(data_for_export, 'Project name', project_data.name)
    data_for_export = _add_single_item_with_label(data_for_export, 'Load source file',
                                                  project_data.load_file_name_by_case[case_name])
    data_for_export = _add_single_item_with_label(data_for_export, 'n users',
                                                  project_data.load_n_users_by_case[case_name])
    data_for_export = _add_single_item_with_label(data_for_export, 'n users',
                                                  project_data.load_n_users_by_case[case_name])
    data_for_export = _add_one_level_dictionary(data_for_export, 'Wholesale price source',
                                                project_data.wholesale_price_info_by_case[case_name])
    data_for_export = _add_one_level_dictionary(data_for_export, 'Demographic filtering',
                                                project_data.filter_options_by_case[case_name])
    result_dataframe_to_export = _merge_results_dataframes(project_data.demographic_info_by_case[case_name],
                                                           project_data.retail_results_by_case[case_name],
                                                           'Demographic', 'Retail')
    result_dataframe_to_export = _merge_results_dataframes(result_dataframe_to_export,
                                                           project_data.network_results_by_case[case_name],
                                                           'Retail', 'Network')
    result_dataframe_to_export = _merge_results_dataframes(result_dataframe_to_export,
                                                           project_data.wholesale_results_by_case[case_name],
                                                           '', 'Wholesale')
    return data_for_export


def _add_single_item_with_label(data_for_export, label, item):
    data_for_export.append([label, item])
    return data_for_export


def _add_one_level_dictionary(data_for_export, label, dictionary):
    data_for_export.append([label])
    for key, value in dictionary.items():
        data_for_export.append([key, value])
    return data_for_export


def _add_results_dataframe(data_for_export, dataframe):
    data_for_export.append(dataframe.columns)
    data_for_export + [[i for i in row] for row in dataframe.itertuples(index=)]
    return data_for_export


def _merge_results_dataframes(left_dataframe, right_dataframe, left_name, right_name):
    left_dataframe = pd.merge(left_dataframe, right_dataframe, how='left', on='CUSTOMER_KEY',
                              suffixes=('_' + left_name, '_' + right_name))
    return left_dataframe


