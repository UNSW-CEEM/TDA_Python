import pandas as pd


def create_sample(gui_inputs, filtered_data):
    # Goal of this function is to create a record of end user tech by customer, should be data frame like. . .
    # CUSTOMER_KEY, HAS_SOLAR, solar_kw, solar_profile_id, HAS_BATTERY, etc
    # ...           ...        ...       ...               ...
    solar_pen = gui_inputs['solar_inputs']['penetration']
    sample_details = {'load_details': gui_inputs['load_details'],
                      'customer_keys': [col for col in filtered_data.columns if col != 'Datetime'],
                      'end_user_tech_details': pd.DataFrame()}
    return sample_details


def set_filtered_data_to_match_saved_sample(end_user_tech):
    return pd.DataFrame()


def calc_net_profiles(gross_load_profiles, end_user_tech):
    return gross_load_profiles
