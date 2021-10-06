import pandas as pd
import data_interface
import numpy as np
import math
import random
import feather
from time import time
import numba
# MAC Added these two below - TODO should they both be using either time or datetime?
# MAC Why do I need to import json, why is it not imported already?
from datetime import datetime
import json
# MAC Added this line below - to get tariff from UI
from data_interface import get_tariff
# Packages below this line can be deleted, used for testing purposes only.
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)


def create_sample(gui_inputs, filtered_data):
    # Goal of this function is to create a record of end user tech by customer, should be data frame like. . .
    # CUSTOMER_KEY, HAS_SOLAR, solar_kw, solar_profile_id, HAS_BATTERY, etc
    # ...           ...        ...       ...               ...

    # This function takes ~2.5secs to execute
    # print("Running create_sample--------------------")

    solar_inputs = gui_inputs['tech_inputs']['solar']
    solar_pen = float(solar_inputs['penetration'])/100.0
    solar_mean_size = float(solar_inputs['mean_size'])
    solar_size_stdev = float(solar_inputs['standard_dev'])
    number_solar_customers = math.ceil(solar_pen * len(filtered_data.columns))

    # @todo: add link to select solar data from solar_profiles folder
    needed_dates = filtered_data.copy()
    needed_dates['Datetime'] = needed_dates.index
    needed_dates = needed_dates.loc[:, ['Datetime']]
    solar_data = solar_inputs['solar_data']
    solar_profiles = feather.read_dataframe('data/solar_profiles/' + solar_data + '.feather')
    solar_profiles = solar_profiles.set_index('Datetime')
    solar_profiles.index = pd.to_datetime(solar_profiles.index)
    solar_orginal_dates = solar_profiles.index
    original_cols = solar_profiles.columns
    solar_profiles = pd.merge(solar_profiles, needed_dates, how='inner',
                              left_on=[solar_profiles.index.month, solar_profiles.index.day,
                                       solar_profiles.index.hour, solar_profiles.index.minute],
                              right_on=[needed_dates.index.month, needed_dates.index.day,
                                        needed_dates.index.hour, needed_dates.index.minute])
    solar_profiles = solar_profiles.set_index('Datetime')
    solar_profiles = solar_profiles.loc[:, original_cols]
    number_solar_profiles = len(solar_profiles.columns)
    solar_profile_ids = solar_profiles.columns.tolist()


    dr_inputs = gui_inputs['tech_inputs']['demand_response']
    #
    dr_pen = float(dr_inputs['penetration'])/100.0
    dr_percent_reduction = float(dr_inputs['mean_load_reduction'])/100.0
    dr_percent_stdev = float(dr_inputs['standard_dev'])/100.0
    dr_mean_response_time = float(dr_inputs['mean_response_time'])
    network_percentage_events_limit = float(dr_inputs['network_percentage_events_limit'])/100
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
        diff = number_solar_customers - number_solar_profiles
        sampled_solar_profile_id += random.choices(solar_profile_ids, k=diff)


    # calculate distribution of solar/battery/demand_response sizes
    solar_system_sizes = np.clip(np.random.normal(solar_mean_size, solar_size_stdev, number_solar_customers), a_min=0, a_max=None)
    dr_percent_reductions = np.clip(np.random.normal(dr_percent_reduction, dr_percent_stdev, number_dr_customers), a_min=0, a_max=None)
    battery_sizes_kW = np.clip(np.random.normal(battery_mean_size, battery_size_stdev, number_battery_customers), a_min=0, a_max=None)
    battery_sizes_kW_to_kWh = np.clip(np.random.normal(battery_pow_to_energy_mean, battery_pow_to_energy_stdev, number_battery_customers), a_min=0, a_max=None)


    end_user_tech_details = pd.DataFrame(
        [],
        columns=['CUSTOMER_KEY', 'HAS_SOLAR', 'solar_kw', 'solar_profile_id',
                 'HAS_BATTERY', 'battery_sizes_kW', 'battery_sizes_kW_to_kWh', 'battery_restriction', 'battery_strategy',
                 'HAS_DR', 'dr_percent_reductions', 'dr_mean_response_time', 'network_percentage_events_limit', 'dr_energy_conservation',
                 ],
        index=filtered_data.columns,
    )


    solar_tech_details = pd.DataFrame(
        {
            'HAS_SOLAR': np.array([True] * number_solar_customers),
            'solar_kw': solar_system_sizes,
            'solar_profile_id': sampled_solar_profile_id
        },
        index=index_solar_customer_id,
    )

    dr_tech_details = pd.DataFrame(
        {
            'HAS_DR': np.array([True] * number_dr_customers),
            'dr_percent_reductions': dr_percent_reductions,
        },
        index=random.sample(list(filtered_data.columns), number_dr_customers),
    )

    battery_tech_details = pd.DataFrame(
        {
            'HAS_BATTERY': np.array([True] * number_battery_customers),
            'battery_sizes_kW': battery_sizes_kW,
            'battery_sizes_kW_to_kWh': battery_sizes_kW_to_kWh,
        },
        index=index_battery_customer_id,
    )

    end_user_tech_details = end_user_tech_details.combine_first(solar_tech_details)
    end_user_tech_details = end_user_tech_details.combine_first(battery_tech_details)
    end_user_tech_details = end_user_tech_details.combine_first(dr_tech_details)
    end_user_tech_details['CUSTOMER_KEY'] = end_user_tech_details.index
    end_user_tech_details = end_user_tech_details.reset_index(drop=True)

    end_user_tech_details[['HAS_BATTERY', 'HAS_DR', 'HAS_SOLAR', 'solar_profile_id']] = end_user_tech_details[['HAS_BATTERY', 'HAS_DR', 'HAS_SOLAR', 'solar_profile_id']].fillna(False)
    end_user_tech_details['battery_restriction'] = end_user_tech_details['battery_restriction'].fillna(battery_restriction)
    end_user_tech_details['battery_strategy'] = end_user_tech_details['battery_strategy'].fillna(battery_strategy)
    end_user_tech_details['dr_mean_response_time'] = end_user_tech_details['dr_mean_response_time'].fillna(dr_mean_response_time)
    end_user_tech_details['network_percentage_events_limit'] = end_user_tech_details['network_percentage_events_limit'].fillna(network_percentage_events_limit)
    end_user_tech_details['dr_energy_conservation'] = end_user_tech_details['dr_energy_conservation'].fillna(dr_energy_conservation)
    end_user_tech_details = end_user_tech_details.fillna(0)

    sample_details = {'load_details': gui_inputs['load_details'],
                      'tech_inputs': gui_inputs['tech_inputs'],
                      'customer_keys': [col for col in filtered_data.columns if col != 'Datetime'],
                      'end_user_tech_details': end_user_tech_details,
                      'solar_profiles': solar_profiles, # @todo: can delete if we store solar profiles already in gui_inputs['tech_inputs']['solar']['profiles']
                      }

    sample_details['message'] = create_message_for_user(solar_orginal_dates, solar_profiles.index)

    return sample_details


def update_sample(current_sample, gui_inputs):
    current_sample['tech_inputs'] = gui_inputs['tech_inputs']
    # just update operation details of sample
    return current_sample


def set_filtered_data_to_match_saved_sample(end_user_tech_sample):
    raw_data = data_interface.get_load_table('/data/load', end_user_tech_sample['load_details']['file_name'])
    filtered_data = raw_data.loc[:, end_user_tech_sample['customer_keys']]
    return pd.DataFrame()


def calc_net_profiles(gross_load_profiles, network_load, end_user_tech, selected_tariff):
    solar_profiles = calc_solar_profiles(end_user_tech)
    net_profile_after_solar = gross_load_profiles - solar_profiles
    net_profile_after_dr = calc_net_profile_after_DR(net_profile_after_solar, network_load, end_user_tech)
    net_profile_after_batt = calc_net_profile_after_battery(net_profile_after_dr, end_user_tech, selected_tariff)
    dr_energy_offset = net_profile_after_solar - net_profile_after_dr
    batt_energy_offset = net_profile_after_dr - net_profile_after_batt
    net_profiles = {'load_profiles': gross_load_profiles,
                    'solar_profiles': solar_profiles,
                    'dr_profiles': dr_energy_offset,
                    'battery_profiles': batt_energy_offset,
                    'final_net_profiles': net_profile_after_batt,
                   }

    return net_profiles


def calc_net_profile_after_battery(net_load_profile, end_user_tech_sample, selected_tariff):
    end_user_tech_details = end_user_tech_sample['end_user_tech_details']
    customer_key = end_user_tech_sample['customer_keys']
    
    net_load_after_batt = net_load_profile.copy()
    number_of_steps = len(net_load_after_batt)

    # @todo: check if we should be allowing users to define these parameters?
    batt_soc = 0.2
    round_trip_batt_eff = 0.85
    single_trip_batt_eff = math.sqrt(round_trip_batt_eff)

    # @todo: check if assumption that batteries charge and discharge at same rate is valid
    if selected_tariff:
        print("MAC selected tariff inside batt_strategy: ------------", type(selected_tariff), selected_tariff)
        print("Net load profile: ---------", type(net_load_profile))#, net_load_profile)
        all_TOU_periods = generate_TOU_periods(selected_tariff, net_load_profile)
        print("generate_TOU_periods run ------------")
        
        peak_assignment = 'Discharge to home'
        shoulder_assignment = 'Charge from grid'
        off_peak_assignment = 'Neither'
        tariff_assignments = {'Peak': peak_assignment, 
                            'Shoulder': shoulder_assignment, 
                            'Off-Peak': off_peak_assignment }
        charging_states = charging_discharging(all_TOU_periods["TOU"], tariff_assignments)
        print("charging_discharging run ------------")
    else:
        print("No tariff selected")
    
    for key in customer_key:
        battery_details = end_user_tech_details.loc[end_user_tech_details['CUSTOMER_KEY'] == key]
        batt_kw = battery_details['battery_sizes_kW'].values[0]
        batt_kw_to_kwh = battery_details['battery_sizes_kW_to_kWh'].values[0]
        batt_strategy = battery_details['battery_strategy'].values[0]

        battery_capacity = 0
        if batt_kw_to_kwh > 0 and batt_kw > 0:
            battery_capacity = batt_kw / batt_kw_to_kwh

        usable_batt_capacity = battery_capacity * (1 - batt_soc)
        current_batt_charge = 0 # inital battery capacity
        max_batt_charge_rate = (batt_kw * single_trip_batt_eff) / 2.0 # current assumes charge and discharge rate is the same
        if batt_strategy == 'Maximise self consumption' and battery_capacity > 0:
            # start2 = time.time()
            current_profile = net_load_after_batt[key].to_numpy()
            new_profile = battery_loop(current_profile, usable_batt_capacity, current_batt_charge, max_batt_charge_rate,
                                       single_trip_batt_eff)
            net_load_after_batt[key] = new_profile
            # end2 = time.time()
            # print('time to calc one battery customer: ', end2-start2)
        elif batt_strategy == 'Minimise costs' and battery_capacity > 0:
            print("MAC going into battery_loop_Miri")
            current_profile = net_load_after_batt[key].to_numpy()
            print("Current profile:-----------", current_profile)
            
            new_profile = battery_loop_Miri(current_profile, usable_batt_capacity, current_batt_charge, max_batt_charge_rate,
                                       single_trip_batt_eff, charging_states)
            print("all_TOU_periods run for 1 house ------------")
            net_load_after_batt[key] = new_profile
    return net_load_after_batt

@numba.jit
def battery_loop(current_profile, usable_batt_capacity, current_batt_charge, max_batt_charge_rate, single_trip_batt_eff):
    print("Regular battery loop is now running-------------")
    n = len(current_profile)
    new_profile = np.empty(n, dtype=np.float64)
    for i in range(n):
        current_power = current_profile[i]
        if current_power < 0:
            # maximum charging rate is batt_kw/2.0 since we are using 30min timestamps
            chargeable_amount = min((usable_batt_capacity - current_batt_charge), max_batt_charge_rate,
                                    abs(current_power))
            new_profile[i] = current_power + chargeable_amount
            current_batt_charge += chargeable_amount * single_trip_batt_eff
        elif current_power > 0:
            dischargeable_amount = min(current_batt_charge, max_batt_charge_rate, current_power)
            new_profile[i] = current_power - dischargeable_amount
            current_batt_charge -= dischargeable_amount / single_trip_batt_eff
        else:
            new_profile[i] = 0
    return new_profile

def generate_TOU_period(selected_tariff, timestamp):
    """
    Looks at individual timestamps, compares them to a TOU tariff to determine 
    if that period is Peak, Off-Peak, or Shoulder
    Args:
        selected_tariff (dictionary): details/rates/times of selected tariff 
        timestamp (datetime): single half-hourly timestamp in datetime format
    Returns:
        TOU_value (string): either Peak, Off-Peak, or Shoulder
    """
    # print("got inside generat_tou-------------weeee")
    TOU = selected_tariff['Parameters']['TOU']
    for key, value in TOU.items():
        # work out if it is peak/off peak/shoulder
        name = key.replace("-", "").replace(" ", "").lower()
        if ('offpeak' in name):
            TOU_value = "Off-Peak"
        elif ('shoulder' in name):
            TOU_value = "Shoulder"
        else:
            TOU_value = "Peak"
        
        # print("got further in generate_tou-------------weeee")
        # work out time
        for k, v in value['TimeIntervals'].items():
            beginning = v[0]
            beg_hour = datetime.strptime(beginning, '%H:%M').time()
            end = v[1]
            # end = '20:00'
            end_hour =  datetime.strptime(end, '%H:%M').time()
            if beg_hour == end_hour and beg_hour == datetime.strptime("00:00", '%H:%M').time():
                beg_hour = datetime.strptime("00:01", '%H:%M').time()
                # print("new end_hour")

            weekday = timestamp.weekday()
            # print("weekday", weekday)
            # print("almost end of generat_tou-------------weeee")
            if beg_hour <= end_hour:
                if (timestamp.time() > beg_hour and timestamp.time() <= end_hour) and (((weekday <= 5 and weekday >=1) and value['Weekday']) or ((weekday == 6 or weekday == 0) and value['Weekend'])):
                    # print("Here:------", TOU_value)
                    return TOU_value
            else:
                if (timestamp.time() > beg_hour or timestamp.time() <= end_hour) and (((weekday <= 5 and weekday >=1) and value['Weekday']) or ((weekday == 6 or weekday == 0) and value['Weekend'])):
                    # print("Here:------", TOU_value)
                    return TOU_value

def generate_TOU_periods(selected_tariff, df):
    """
    Compiles all Peak/Off-Peak/Shoulder values into longer array for every half-hourly period in the year
    Args:
        selected_tariff (dictionary): details/rates/times of selected tariff 
        df (dataframe): dataframe of entire load profiles including timestamp
    Returns:
        TOU_values (array): a list of strings of Peak, Off-Peak, or Shoulder, likely 17520 length
    """
    print("net_load_profile.shape:---------", df.shape)
    df = df.reset_index()
    df = df.rename(columns={'index': 'Datetime'})
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    # Generate new df
    df['TOU'] = "Off Peak"
    TOU_periods = df[['Datetime', 'TOU']].copy()
    TOU_periods['TOU'] = df.apply(lambda x: generate_TOU_period(selected_tariff, x['Datetime']),axis=1)
    return TOU_periods

def charging_discharging(TOU_periods,tariff_assignments):
    """
    Depending on user-determined charging/discharging, assigns Peak/Off-Peak/Shoulder periods to a charging state
    Args:
        TOU_values (array): a list of strings of Peak, Off-Peak, or Shoulder, likely 17520 length (from generate_TOU_periods)
        tariff_assignments (dictionary): assigns Peak/Off-Peak/Shoulder to charging or discharging (direct user input)
    Returns:
        charging_states (array): list of "Discharge to home"/"Charging from grid"/"Neither", 17520 length
    """
    # MAC TOU_periods = array of length 17520 listing period as peak, off peak, or shoulder
    n = len(TOU_periods)
    charging_states = []
    for i in range(n):     
        TOU_period = TOU_periods[i]
        charging_states.append(tariff_assignments[TOU_period])
    return charging_states

def battery_loop_Miri(current_profile, usable_batt_capacity, current_batt_charge, max_batt_charge_rate, 
                        single_trip_batt_eff, charging_states):
    # need to add 'charging_state' vector of length n defined CH/DCH for each i, for now adding in below:
    """
    Runs battery loop depending on charging/discharging state determined by user
    Args:
        current_profile (array): single home's half-hourly energy profile
        usable_batt_capacity (float): useable battery capacity in kWh (eg. 13.5 kWh for Powerwall 2)
        current_batt_charge (float): battery starting value in kWh, likely 0 (defined somewhere in TDA)
        max_batt_charge_rate (float): maximum power rating in kW (eg. 5 kW for Powerwall 2)
        single_trip_batt_eff (float): battery's single trip efficiency, square root of round trip efficiency
        charging_states (array): list of "Discharge to home"/"Charging from grid"/"Neither", 17520 length
    Returns:
        new_profile (array): single home's half-hourly energy profile after battery loop runs
    """
    print("Miri battery loop is now running------------------")
    n = len(current_profile)
    new_profile = np.empty(n, dtype=np.float64)  
    for i in range(n):
        current_power = current_profile[i]
        # WANT current_time = times[i]
        # print("Iteration:", i+1)
        # print("Half-hourly demand:", current_power)
        # Initialise relevant values:
        PV_chargeable_amount = 0
        grid_chargeable_amount = 0
        dischargeable_amount = 0
        charging_state = charging_states[i]
        # When there is excess solar, battery charges:
        if current_power < 0: # that is, there is excess solar
            # maximum charging rate is batt_kw/2.0 since we are using 30min timestamps
            PV_chargeable_amount = min((usable_batt_capacity - current_batt_charge), max_batt_charge_rate,
                                    abs(current_power))
                                    # battery adds whatever can a) fit b) charge c) is available
            current_batt_charge += PV_chargeable_amount * single_trip_batt_eff #updates battery aggregate
            # print("PV chargeable amount:", PV_chargeable_amount)
            # print("Battery charge after PV:", current_batt_charge)
        # If in CH, charges from grid, if in DCH, discharges to house:
        if charging_state == 'Charge from grid':
            grid_chargeable_amount = min((usable_batt_capacity - current_batt_charge), 
                                        (max_batt_charge_rate - PV_chargeable_amount))
                                    # battery charges from grid whatever can a) fit b) charge
            current_batt_charge += grid_chargeable_amount * single_trip_batt_eff #updates battery aggregate
            # print("Grid chargeable amount:", grid_chargeable_amount)
            # print("Battery charge after grid:", current_batt_charge)
        elif charging_state == 'Discharge to home' and current_power >= 0:
            dischargeable_amount = min(current_batt_charge, max_batt_charge_rate, current_power)
                                    #MAC: need to specify not in current_power is neg; then doesn't discharge at all
                                    # battery discharges whatever a) is left b) can discharge c) is needed
            current_batt_charge -= dischargeable_amount / single_trip_batt_eff #updates battery aggregate
                    #MAC does this mean that it can take out more than is actually in the battery?
            # print("Dischargeable amount:", dischargeable_amount)
            # print("Battery charge after home:", current_batt_charge)
        # Aggregate profile after all processes:
        new_profile[i] = current_power + PV_chargeable_amount + grid_chargeable_amount - dischargeable_amount
        # print("New profile:", new_profile[i])
    return new_profile

def calc_solar_profiles(end_user_tech_sample):
    end_user_tech_details = end_user_tech_sample['end_user_tech_details']
    solar_profiles = end_user_tech_sample['solar_profiles'].clip(0)
    customer_key = end_user_tech_sample['customer_keys']

    solar_kwh_profiles = []
    columns = []
    zero_profile = pd.Series(np.zeros(len(solar_profiles)), index=solar_profiles.index)
    for key in customer_key:
        solar_details = end_user_tech_details.loc[end_user_tech_details['CUSTOMER_KEY'] == key]
        solar_profile_id = solar_details['solar_profile_id'].values[0]
        solar_kw = solar_details['solar_kw'].values[0]
        if solar_profile_id:
            solar_kwh_profiles.append(solar_profiles[solar_profile_id] * solar_kw)
        else:
            solar_kwh_profiles.append(zero_profile)
        columns.append(key)
    solar_kwh_profiles = pd.DataFrame({key: series for key, series in zip(columns, solar_kwh_profiles)})
    return solar_kwh_profiles


def calc_net_profile_after_DR(load_profile, network_load, end_user_tech_sample):

    end_user_tech_details = end_user_tech_sample['end_user_tech_details']
    customer_key = end_user_tech_sample['customer_keys']
    network_percentage_events_limit = end_user_tech_details['network_percentage_events_limit'][0]
    dr_mean_response_time = end_user_tech_details['dr_mean_response_time'][0]
    dr_energy_conservation = end_user_tech_details['dr_energy_conservation'][0]

    net_load_after_dr = load_profile.copy()
    ##########################################
    # Check for valid inputs
    if network_percentage_events_limit <= 0 or dr_mean_response_time <= 0:
        return net_load_after_dr

    ##########################################
    # Time settings for response time and period of demand response
    dr_response_time = pd.Timedelta(dr_mean_response_time, unit='hour')
    start_time_diff = (dr_response_time / 2).floor('30min')
    end_time_diff = (dr_response_time / 2).ceil('30min')

    #####################################
    # Find event limit in kw
    dr_network_kwh_limit = network_percentage_events_limit * network_load['load'].max()


    ###############################
    # Currently assumes one demand response event per day over the dr_network_kw_limit
    daily_peak_demand = network_load.loc[network_load.groupby(pd.Grouper(freq='D')).idxmax().iloc[:, 0]]
    dr_event_days = daily_peak_demand[daily_peak_demand['load'] > dr_network_kwh_limit]
    t0 = time()
    rebound_hours = 6
    response_time_indexes_by_day = []
    for day in dr_event_days.index:
        mask1 = (net_load_after_dr.index >= (day - start_time_diff)) & \
                (net_load_after_dr.index <= (day + end_time_diff))
        response_time_indexes_by_day.append(np.nonzero(mask1)[0])
    #response_time_indexes_by_day = np.vstack(response_time_indexes_by_day)

    rebound_time_indexes_by_day = []
    for day in dr_event_days.index:
        start1 = day + end_time_diff
        end1 = start1 + pd.Timedelta(rebound_hours, unit='hour')
        mask2 = (net_load_after_dr.index > start1) & (net_load_after_dr.index <= end1)
        rebound_time_indexes_by_day.append(np.nonzero(mask2)[0])
    #rebound_time_indexes_by_day = np.vstack(rebound_time_indexes_by_day)

    rebound_distribution = np.random.weibull(2, rebound_hours*2)

    for key in customer_key:
        dr_details = end_user_tech_details.loc[end_user_tech_details['CUSTOMER_KEY'] == key]
        dr_percent_load_reduction = dr_details['dr_percent_reductions'].values[0]
        current_profile = net_load_after_dr[key].to_numpy()
        net_load_after_dr[key] = do_demand_response(current_profile, response_time_indexes_by_day,
                                                    rebound_time_indexes_by_day, dr_percent_load_reduction,
                                                    rebound_distribution, dr_energy_conservation,
                                                    dr_mean_response_time)

    return net_load_after_dr


def do_demand_response(current_profile, response_time_indexes_by_day,  rebound_time_indexes_by_day,
                       dr_percent_load_reduction, rebound_distribution, dr_energy_conservation, dr_mean_response_time):
    n = len(response_time_indexes_by_day)
    for i in range(n):
        energy_offset = max(max(current_profile[response_time_indexes_by_day[i]]) * dr_percent_load_reduction, 0)
        current_profile[response_time_indexes_by_day[i]] = \
            current_profile[response_time_indexes_by_day[i]] - energy_offset
        total_energy_offset = energy_offset * dr_mean_response_time
        if dr_energy_conservation == 'Yes':
            if len(rebound_distribution) != len(rebound_time_indexes_by_day[i]):
                rebound_distribution = rebound_distribution[:len(rebound_time_indexes_by_day[i])]
            scale = total_energy_offset / rebound_distribution.sum()
            current_profile[rebound_time_indexes_by_day[i]] = current_profile[rebound_time_indexes_by_day[i]] + \
                sort_from_middle(np.sort(rebound_distribution * scale)[::-1],
                                 int(len(rebound_time_indexes_by_day[i]) * (2/3)))
    return current_profile


def sort_from_middle(arr, n):
    arr1 = sorted(arr[:n // 2])
    arr2 = sorted(arr[n // 2:], reverse=True)
    return arr1 + arr2


def create_message_for_user(original_solar_dates, new_solar_dates):
    start_solar = np.min(original_solar_dates)
    end_solar = np.max(original_solar_dates)
    start_load = np.min(new_solar_dates)
    end_load = np.max(new_solar_dates)
    overlapping_dates = np.intersect1d(original_solar_dates, new_solar_dates)
    overlap_percentage = round(((1 - len(overlapping_dates)/len(new_solar_dates))) * 100, 0)
    if overlap_percentage != 0.0:
        message = '''Please note a {}% of the solar data used is drawn from a different calender year to the load data.
                  The load data comes from between {} to {}, 
                  and the solar data from {} to {}. The two data sets have 
                  been merged on a month, day, hour and minute basis.'''.format(overlap_percentage, start_load, end_load,
                                                                                start_solar, end_solar)
    else:
        message = 'Done!'
    return message
