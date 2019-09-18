import pandas as pd
import data_interface
import numpy as np
import math
import random

# Packages below this line can be deleted, used for testing purposes only.
import time
pd.set_option('display.max_rows', 100)

def create_sample(gui_inputs, filtered_data):
    # Goal of this function is to create a record of end user tech by customer, should be data frame like. . .
    # CUSTOMER_KEY, HAS_SOLAR, solar_kw, solar_profile_id, HAS_BATTERY, etc
    # ...           ...        ...       ...               ...

    # This function takes ~2.5secs to execute
    # print('gui_inputs: ', gui_inputs)

    solar_inputs = gui_inputs['tech_inputs']['solar']
    #
    solar_pen = float(solar_inputs['penetration'])/100.0
    solar_mean_size = float(solar_inputs['mean_size'])
    solar_size_stdev = float(solar_inputs['standard_dev'])
    number_solar_customers = math.ceil(solar_pen * len(filtered_data.columns))

    # @todo: add link to select solar data from solar_profiles folder
    # solar_profiles = solar_inputs['profiles']
    solar_profiles = pd.read_csv('data/solar_profiles/solar_profile.csv')
    solar_profiles = solar_profiles.set_index('Datetime')
    solar_profiles.index = pd.to_datetime(solar_profiles.index)
    number_solar_profiles = len(solar_profiles.columns)
    solar_profile_ids = solar_profiles.columns.tolist()


    dr_inputs = gui_inputs['tech_inputs']['demand_response']
    #
    dr_pen = float(dr_inputs['penetration'])/100.0
    dr_mean_size = float(dr_inputs['mean_size'])
    dr_size_stdev = float(dr_inputs['standard_dev'])
    dr_max_response_time = float(dr_inputs['max_response_time'])
    dr_events_limit = float(dr_inputs['events_limit'])
    dr_energy_conservation = dr_inputs['energy_conservation']
    number_dr_customers = math.ceil(dr_pen * len(filtered_data.columns))


    battery_inputs = gui_inputs['tech_inputs']['battery']
    #
    battery_pen = float(battery_inputs['penetration'])/100.0
    battery_mean_size = float(battery_inputs['mean_size'])
    battery_size_stdev = float(battery_inputs['standard_dev'])
    battery_pow_to_energy_mean = float(battery_inputs['mean_power_to_energy'])
    battery_pow_to_energy_stdev = float(battery_inputs['power_to_energy_standard_dev'])
    battery_restriction = battery_inputs['restriction']
    battery_strategy = battery_inputs['strategy']
    number_battery_customers = math.ceil(battery_pen * len(filtered_data.columns))

    if battery_restriction == 'Customers with solar':
        if number_solar_customers >= number_battery_customers:
            index_solar_customer_id = random.sample(list(filtered_data.columns), number_solar_customers)
            index_battery_customer_id = random.sample(index_solar_customer_id, number_battery_customers)
        else:
            # @todo: check if battery restriction by customers with solar limits number of battery
            number_battery_customers = number_solar_customers
            index_battery_customer_id = random.sample(list(filtered_data.columns), number_battery_customers)
            index_solar_customer_id = random.sample(index_battery_customer_id, number_solar_customers)
    else:
        index_solar_customer_id = random.sample(list(filtered_data.columns), number_solar_customers)
        index_battery_customer_id = random.sample(list(filtered_data.columns), number_battery_customers)


    # select solar_profile_ids randomly that maximises the number of unique solar_profile_ids to each customer
    if number_solar_profiles >= number_solar_customers:
        sampled_solar_profile_id = random.sample(solar_profile_ids, number_solar_customers)
    elif number_solar_profiles < number_solar_customers:
        sampled_solar_profile_id = random.sample(solar_profile_ids, number_solar_profiles)
        diff = number_solar_profiles - number_solar_customers
        sampled_solar_profile_id.append(random.choices(solar_profile_ids, k=diff))


    # calculate distribution of solar/battery/demand_response sizes
    solar_system_sizes = np.random.normal(solar_mean_size, solar_size_stdev, number_solar_customers).tolist()
    dr_sizes = np.random.normal(dr_mean_size, dr_size_stdev, number_dr_customers).tolist()
    battery_sizes_kW = np.random.normal(battery_mean_size, battery_size_stdev, number_battery_customers).tolist()
    battery_sizes_kW_to_kWh = np.random.normal(battery_pow_to_energy_mean, battery_pow_to_energy_stdev, number_battery_customers).tolist()


    end_user_tech_details = pd.DataFrame(
        [],
        columns=['CUSTOMER_KEY', 'HAS_SOLAR', 'solar_kw', 'solar_profile_id',
                 'HAS_BATTERY', 'battery_sizes_kW', 'battery_sizes_kW_to_kWh', 'battery_restriction', 'battery_strategy',
                 'HAS_DR', 'dr_sizes', 'dr_max_response_time', 'dr_events_limit', 'dr_energy_conservation',
                 ],
        index=filtered_data.columns,
    )

    solar_tech_details = pd.DataFrame(
        {
            'HAS_SOLAR': np.full((1, number_solar_customers), True)[0].tolist(),
            'solar_kw': solar_system_sizes,
            'solar_profile_id': sampled_solar_profile_id
        },
        index=index_solar_customer_id,
    )

    # @todo: check how max response time is calculated
    dr_tech_details = pd.DataFrame(
        {
            'HAS_DR': np.full((1, number_dr_customers), True)[0].tolist(),
            'dr_sizes': dr_sizes,
            'dr_max_response_time': dr_max_response_time,
            'dr_events_limit': dr_events_limit,
            'dr_energy_conservation': dr_energy_conservation,
        },
        index=random.sample(list(filtered_data.columns), number_dr_customers),
    )

    battery_tech_details = pd.DataFrame(
        {
            'HAS_BATTERY': np.full((1, number_battery_customers), True)[0].tolist(),
            'battery_sizes_kW': battery_sizes_kW,
            'battery_sizes_kW_to_kWh': battery_sizes_kW_to_kWh,
            'battery_restriction': [battery_restriction] * number_battery_customers,
            'battery_strategy': [battery_strategy] * number_battery_customers,
        },
        index=index_battery_customer_id,
    )

    end_user_tech_details = end_user_tech_details.combine_first(solar_tech_details)
    end_user_tech_details = end_user_tech_details.combine_first(battery_tech_details)
    end_user_tech_details = end_user_tech_details.combine_first(dr_tech_details)
    end_user_tech_details['CUSTOMER_KEY'] = end_user_tech_details.index
    end_user_tech_details = end_user_tech_details.reset_index(drop=True)

    sample_details = {'load_details': gui_inputs['load_details'],
                      'tech_inputs': gui_inputs['tech_inputs'],
                      'customer_keys': [col for col in filtered_data.columns if col != 'Datetime'],
                      'end_user_tech_details': end_user_tech_details,
                      'solar_profiles': solar_profiles, # @todo: can delete if we store solar profiles already in gui_inputs['tech_inputs']['solar']['profiles']
                      }
    return sample_details


def update_sample(current_sample, gui_inputs):
    current_sample['tech_inputs'] = gui_inputs['tech_inputs']
    # just update operation details of sample
    return current_sample


def set_filtered_data_to_match_saved_sample(end_user_tech_sample):
    raw_data = data_interface.get_load_table('/data/load', end_user_tech_sample['load_details']['file_name'])
    filtered_data = raw_data.loc[:, end_user_tech_sample['customer_keys']]
    return pd.DataFrame()


def calc_net_profiles(gross_load_profiles, end_user_tech):
    customer_solar_profiles = calc_solar_profiles(end_user_tech)

    net_profile = calc_net_profile_after_DR(gross_load_profiles, end_user_tech)
    net_profile = calc_net_profile_after_battery(net_profile, customer_solar_profiles, end_user_tech)

    return net_profile


def calc_net_profile_after_battery(load_profile, solar_profile, end_user_tech_sample):
    end_user_tech_details = end_user_tech_sample['end_user_tech_details']
    customer_key = end_user_tech_sample['customer_keys']

    # @todo: check if we should be allowing users to define these parameters?
    batt_soc = 0.2
    round_trip_batt_eff = 0.85
    single_trip_batt_eff = math.sqrt(round_trip_batt_eff)

    # @todo: check if assumption that batteries charge and discharge at same rate is valid
    new_profile_after_batt = pd.DataFrame([])

    for key in customer_key:
        battery_details = end_user_tech_details.loc[end_user_tech_details['CUSTOMER_KEY'] == key]
        batt_kw = battery_details['battery_sizes_kW'].values[0]
        batt_kw_to_kwh = battery_details['battery_sizes_kW_to_kWh'].values[0]
        batt_strategy = battery_details['battery_strategy'].values[0]

        battery_capacity = 0
        if str(batt_kw_to_kwh) != 'nan' and str(batt_kw) != 'nan':
            if batt_kw_to_kwh > 0:
                battery_capacity = batt_kw / batt_kw_to_kwh

        usable_batt_capacity = battery_capacity * (1 - batt_soc)
        current_batt_charge = 0 # inital battery capacity
        max_batt_charge_rate = (batt_kw * single_trip_batt_eff) / 2.0 # current assumes charge and discharge rate is the same

        new_profile = load_profile[[key]] - solar_profile[[key]]
        if batt_strategy == 'Maximise self consumption':
            # start2 = time.time()
            for i in range(1, len(new_profile)):
                net_profile = new_profile[key][i]
                if net_profile < 0:
                    # maximum charging rate is batt_kw/2.0 since we are using 30min timestamps
                    chargeable_amount = min((usable_batt_capacity - current_batt_charge), max_batt_charge_rate, abs(net_profile))
                    new_profile[key][i] = net_profile + chargeable_amount
                    current_batt_charge += chargeable_amount / single_trip_batt_eff
                elif net_profile > 0:
                    dischargeable_amount = min(current_batt_charge, max_batt_charge_rate, net_profile)
                    new_profile[key][i] = net_profile - dischargeable_amount
                    current_batt_charge -= dischargeable_amount / single_trip_batt_eff
                else:
                    pass
            # end2 = time.time()
            # print('time to calc one customer: ', end2-start2)

        new_profile_after_batt = pd.concat(
            [new_profile_after_batt, new_profile], axis=1)

    return new_profile_after_batt


def calc_solar_profiles(end_user_tech_sample):

    end_user_tech_details = end_user_tech_sample['end_user_tech_details']
    solar_profiles = end_user_tech_sample['solar_profiles'].clip(0)
    customer_key = end_user_tech_sample['customer_keys']

    solar_kwh_profiles = pd.DataFrame([])
    for key in customer_key:
        solar_details = end_user_tech_details.loc[end_user_tech_details['CUSTOMER_KEY'] == key]
        solar_profile_id = solar_details['solar_profile_id'].values[0]
        solar_kw = solar_details['solar_kw'].values[0]

        if str(solar_profile_id) != 'nan':
            solar_kwh_profiles = pd.concat([solar_kwh_profiles, solar_profiles[[solar_profile_id]].rename(columns={solar_profile_id: key}) * solar_kw], axis=1)
        else:
            solar_kwh_profiles = pd.concat(
                [solar_kwh_profiles, pd.DataFrame(np.zeros((len(solar_profiles), 1)), index=solar_profiles.index, columns=[key])], axis=1)

    return solar_kwh_profiles


def calc_net_profile_after_DR(load_profile, end_user_solar_tech):
    return load_profile


