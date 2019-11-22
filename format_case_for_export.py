import pandas as pd


def process_case(case_name, project_data):
    data_for_export = []
    data_for_export = _add_single_item_with_label(data_for_export, 'Project name', project_data.name)
    data_for_export = _add_single_item_with_label(data_for_export, 'Load source file',
                                                  project_data.load_file_name_by_case[case_name])
    data_for_export = _add_single_item_with_label(data_for_export, 'n users',
                                                  project_data.load_n_users_by_case[case_name])
    if case_name in project_data.wholesale_price_info_by_case.keys():
        data_for_export = _add_one_level_dictionary(data_for_export, 'Wholesale price source',
                                                    project_data.wholesale_price_info_by_case[case_name])
    if case_name in project_data.retail_tariffs_by_case.keys():
        data_for_export = _add_single_item_with_label(data_for_export, 'Retail tariff',
                                                      project_data.retail_tariffs_by_case[case_name]['Name'])
    if case_name in project_data.network_tariffs_by_case.keys():
        data_for_export = _add_single_item_with_label(data_for_export, 'Network tariff',
                                                      project_data.network_tariffs_by_case[case_name]['Name'])
    data_for_export = _add_one_level_dictionary(data_for_export, 'Demographic filtering',
                                                project_data.filter_options_by_case[case_name])
    #result_dataframe_to_export = \
    #    project_data.demographic_info_by_case[case_name].add_prefix('Demographic_').rename(
    #        columns={'Demographic_CUSTOMER_KEY': 'CUSTOMER_KEY'})
    if case_name in project_data.retail_results_by_case.keys():
        retail_results = project_data.retail_results_by_case[case_name]['Retailer'].add_prefix('Retailer_').reset_index()
        #result_dataframe_to_export = _merge_results_dataframes(result_dataframe_to_export, retail_results)
        result_dataframe_to_export = retail_results
    if case_name in project_data.network_results_by_case.keys():
        duos_results = project_data.network_results_by_case[case_name]['DUOS'].add_prefix('DUOS_').reset_index()
        tuos_results = project_data.network_results_by_case[case_name]['TUOS'].add_prefix('TUOS_').reset_index()
        nuos_results = project_data.network_results_by_case[case_name]['NUOS'].add_prefix('NUOS_').reset_index()
        result_dataframe_to_export = _merge_results_dataframes(result_dataframe_to_export, duos_results)
        result_dataframe_to_export = _merge_results_dataframes(result_dataframe_to_export, tuos_results)
        result_dataframe_to_export = _merge_results_dataframes(result_dataframe_to_export, nuos_results)
    if case_name in project_data.wholesale_results_by_case.keys():
        wholesale_result_dataframe_to_export = \
            project_data.wholesale_results_by_case[case_name].add_prefix('Wholesale_').rename(
                columns={'Wholesale_CUSTOMER_KEY': 'CUSTOMER_KEY'})
        result_dataframe_to_export = _merge_results_dataframes(result_dataframe_to_export,
                                                               wholesale_result_dataframe_to_export)
    data_for_export = _add_results_dataframe(data_for_export, result_dataframe_to_export)
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
    data_for_export.append(list(dataframe.columns))
    data_for_export += dataframe.values.tolist()
    return data_for_export


def _merge_results_dataframes(left_dataframe, right_dataframe):
    left_dataframe = pd.merge(left_dataframe, right_dataframe, how='left', on='CUSTOMER_KEY')
    return left_dataframe


