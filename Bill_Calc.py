import numpy as np
import pandas as pd
import time


# https://github.com/UNSW-CEEM/Bill_Calculator
#
# Inputs: Tariff and Load profile (30 min interval, one year,
# timestamps are the end of time period: 12:30 is consumption from 12 to 12:30)
# If tariff rates include gst the result will be gst inclusive
# if discount applies to any rate, it should be considered before calling the function

def bill_calculator(load_profile, tariff, network_load=None, fit=True):

    # Treating load profile

    load_profile = load_profile.fillna(0)

    def time_select(load_profile_s, par):
        load_profile_s_t_a = pd.DataFrame()
        for k2_1, v2_1, in par['TimeIntervals'].items():
            if v2_1[0][0:2] == '24':
                v2_1[0] = v2_1[1].replace("24", "00")
            if v2_1[1][0:2] == '24':
                v2_1[1] = v2_1[1].replace("24", "00")
            if v2_1[0] != v2_1[1]:
                load_profile_s_t = load_profile_s.between_time(start_time=v2_1[0], end_time=v2_1[1], include_start=False,
                                                           include_end=True)
            else:
                load_profile_s_t = load_profile_s.copy()

            if not par['Weekday']:
                load_profile_s_t = load_profile_s_t.loc[load_profile_s_t.index.weekday >= 5].copy()

            if not par['Weekend']:
                load_profile_s_t = load_profile_s_t.loc[load_profile_s_t.index.weekday < 5].copy()

            load_profile_s_t = load_profile_s_t.loc[load_profile_s_t.index.month.isin(par['Month']), :].copy()

            load_profile_s_t_a = pd.concat([load_profile_s_t_a, load_profile_s_t])
        return load_profile_s_t_a

    # Calculate imports and exports
    results = {}
    imports = [np.nansum(load_profile[col].values[load_profile[col].values > 0])
               for col in load_profile.columns]
    results['LoadInfo'] = pd.DataFrame(index=[col for col in load_profile.columns],
                                       data=imports, columns=['Annual_kWh'])
    if fit:
        exports = [np.nansum(load_profile[col].values[load_profile[col].values < 0])
                   for col in load_profile.columns]
        results['LoadInfo']['Annual_kWh_exp'] = [x for x in exports]

    # If it is retailer put retailer as a component to make it similar to network tariffs
    if tariff['ProviderType'] == 'Retailer':
        tariff_temp = tariff.copy()
        del tariff_temp['Parameters']
        tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
        tariff = tariff_temp.copy()

    for TarComp, TarCompVal in tariff['Parameters'].items():
        results[TarComp] = pd.DataFrame(index=results['LoadInfo'].index)

    # Calculate the FiT
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'FiT' in TarCompVal.keys():
            results[TarComp]['Charge_FiT_Rebate'] = results['LoadInfo']['Annual_kWh_exp'] * TarCompVal['FiT']['Value']

    # Check if daily exists and calculate the charge
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'Daily' in TarCompVal.keys():
            num_days = (len(load_profile.index.normalize().unique()) - 1)
            break
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'Daily' in TarCompVal.keys():
            results[TarComp]['Charge_Daily'] = num_days * TarCompVal['Daily']['Value']

    # Energy
    # Flat Rate:
    # Check if flat rate charge exists and calculate the charge
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'FlatRate' in TarCompVal.keys():
            results[TarComp]['Charge_FlatRate'] = results['LoadInfo']['Annual_kWh'] * TarCompVal['FlatRate']['Value']


    # Block Annual:
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'BlockAnnual' in TarCompVal.keys():
            block_use = results['LoadInfo'][['Annual_kWh']].copy()
            block_use_charge = block_use.copy()
            # separating the blocks of usage
            lim = 0
            for k, v in TarCompVal['BlockAnnual'].items():
                block_use[k] = block_use['Annual_kWh']
                block_use[k][block_use[k] > v['HighBound']] = v['HighBound']
                block_use[k] = block_use[k] - lim
                block_use[k][block_use[k] < 0] = 0
                lim = v['HighBound']
                block_use_charge[k] = block_use[k] * v['Value']
            del block_use['Annual_kWh']
            del block_use_charge['Annual_kWh']
            results[TarComp]['Charge_BlockAnnual'] = block_use_charge.sum(axis=1)

    # Block Quarterly:
    # check if it has quarterly and if yes calculate the quarterly energy
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'BlockQuarterly' in TarCompVal.keys():
            for Q in range(1, 5):
                load_profile_q = load_profile.loc[
                                 load_profile.index.month.isin(list(range((Q - 1) * 3 + 1, Q * 3 + 1))), :]
                results['LoadInfo']['kWh_Q' + str(Q)] = [
                    np.nansum(load_profile_q[col].values[load_profile_q[col].values > 0])
                    for col in load_profile_q.columns]
            break

    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'BlockQuarterly' in TarCompVal.keys():
            for Q in range(1, 5):
                block_use = results['LoadInfo'][['kWh_Q' + str(Q)]].copy()
                block_use_charge = block_use.copy()
                lim = 0
                for k, v in TarCompVal['BlockQuarterly'].items():
                    block_use[k] = block_use['kWh_Q' + str(Q)]
                    block_use[k][block_use[k] > v['HighBound']] = v['HighBound']
                    block_use[k] = block_use[k] - lim
                    block_use[k][block_use[k] < 0] = 0
                    lim = v['HighBound']
                    block_use_charge[k] = block_use[k] * v['Value']
                del block_use['kWh_Q' + str(Q)]
                del block_use_charge['kWh_Q' + str(Q)]
                results[TarComp]['C_Q' + str(Q)] = block_use_charge.sum(axis=1)
            results[TarComp]['Charge_BlockQuarterly'] = results[TarComp][
                ['C_Q' + str(Q) for Q in range(1, 5)]].sum(axis=1)

    # Block Monthly:
    # check if it has Monthly and if yes calculate the Monthly energy
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'BlockMonthly' in TarCompVal.keys():
            for m in range(1, 13):
                load_profile_m = load_profile.loc[load_profile.index.month == m, :]
                results['LoadInfo']['kWh_m' + str(m)] = [
                    np.nansum(load_profile_m[col].values[load_profile_m[col].values > 0])
                    for col in load_profile_m.columns]
            break

    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'BlockMonthly' in TarCompVal.keys():
            for Q in range(1, 13):
                block_use = results['LoadInfo'][['kWh_m' + str(Q)]].copy()
                block_use_charge = block_use.copy()
                lim = 0
                for k, v in TarCompVal['BlockMonthly'].items():
                    block_use[k] = block_use['kWh_m' + str(Q)]
                    block_use[k][block_use[k] > v['HighBound']] = v['HighBound']
                    block_use[k] = block_use[k] - lim
                    block_use[k][block_use[k] < 0] = 0
                    lim = v['HighBound']
                    block_use_charge[k] = block_use[k] * v['Value']
                del block_use['kWh_m' + str(Q)]
                del block_use_charge['kWh_m' + str(Q)]
                results[TarComp]['C_m' + str(Q)] = block_use_charge.sum(axis=1)
            results[TarComp]['Charge_BlockMonthly'] = results[TarComp][['C_m' + str(Q) for Q in range(1, 13)]].sum(
                axis=1)

    # Block Daily:
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'BlockDaily' in TarCompVal.keys():
            DailykWh = load_profile.resample('D').sum()
            block_use_temp_charge = DailykWh.copy()
            block_use_temp_charge.iloc[:, :] = 0
            lim = 0
            for k, v in TarCompVal['BlockDaily'].items():
                block_use_temp = DailykWh.copy()
                block_use_temp[block_use_temp > v['HighBound']] = v['HighBound']
                block_use_temp = block_use_temp - lim
                block_use_temp[block_use_temp < 0] = 0
                lim = v['HighBound']
                block_use_temp_charge = block_use_temp_charge + block_use_temp * v['Value']
            results[TarComp]['Charge_BlockDaily'] = block_use_temp_charge.sum(axis=0)


    # TOU energy
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'TOU' in TarCompVal.keys():
            load_profile_ti = pd.DataFrame()
            load_profile_ti_charge = pd.DataFrame()
            for k, v in TarCompVal['TOU'].items():
                this_part = v.copy()
                if 'Weekday' not in this_part:
                    this_part['Weekday'] = True
                    this_part['Weekend'] = True
                if 'TimeIntervals' not in this_part:
                    this_part['TimeIntervals'] = {'T1': ['00:00', '00:00']}
                if 'Month' not in this_part:
                    this_part['TimeIntervals'] = list(range(1, 13))
                load_profile_t_a = time_select(load_profile, this_part)
                load_profile_ti[k] = load_profile_t_a.sum()
                results[TarComp]['kWh_' + k] = load_profile_ti[k]
                load_profile_ti_charge[k] = this_part['Value'] * load_profile_ti[k]
                results[TarComp]['C_' + k] = load_profile_ti_charge[k]
            results[TarComp]['Charge_TOU'] = load_profile_ti_charge.sum(axis=1)

    # Demand charge:
    for TarComp, TarCompVal in tariff['Parameters'].items():
        if 'Demand' in TarCompVal.keys():
            for DemCharComp, DemCharCompVal in TarCompVal['Demand'].items():
                ts_num = DemCharCompVal['Demand Window Length']  # number of timestamp
                num_of_peaks = DemCharCompVal['Number of Peaks']
                if ts_num > 1:
                    load_profile_r = load_profile.rolling(ts_num, min_periods=1).mean()
                else:
                    load_profile_r = load_profile.copy()
                load_profile_f = time_select(load_profile_r, DemCharCompVal)

                # if capacity charge is applied meaning the charge only applies when you exceed the capacity for
                #  a certain number of times
                if 'Capacity' in DemCharCompVal:
                    # please note the capacity charge only works with user's demand peak (not coincident peak)
                    # Customers can exceed their capacity level on x separate days per month during each interval
                    # (day or night). If they exceed more than x times, they will be charged for the highest
                    # exceedance of their capacity the capacity charge (if they don't exceed) is already included
                    # in the fixed charge so they only pay for the difference
                    capacity = DemCharCompVal['Capacity']['Value']
                    if 'Capacity Exceeded No' in DemCharCompVal:
                        cap_exc_no = DemCharCompVal['Capacity Exceeded No']
                    else:
                        cap_exc_no = 0
                    load_profile_f = load_profile_f - (capacity / 2)
                    load_profile_f = load_profile_f.clip(lower=0)
                    load_profile_f_g = load_profile_f.groupby(load_profile_f.index.normalize()).max()
                    for m in range(1, 13):
                        arr = load_profile_f_g.loc[load_profile_f_g.index.month == m, :].copy().values
                        cap_exc_no_val = np.sum(arr > 0, axis=0)
                        load_profile_f.loc[load_profile_f.index.month == m, cap_exc_no_val <= cap_exc_no] = 0
                    load_profile_f2 = load_profile_f.copy()
                else:
                    load_profile_f2 = load_profile_f.copy()
                based_on_network_peak = False
                if 'Based on Network Peak' in DemCharCompVal:
                    if DemCharCompVal['Based on Network Peak']:
                        based_on_network_peak = True
                # minimum demand or demand charge
                min_dem1 = 0
                min_dem2 = 0
                if 'Min Demand (kW)' in DemCharCompVal:
                    min_dem1 = DemCharCompVal['Min Demand (kW)']
                if 'Min Demand Charge ($)' in DemCharCompVal:
                    if DemCharCompVal['Value'] > 0:
                        min_dem2 = DemCharCompVal['Min Demand Charge ($)'] / DemCharCompVal['Value']
                min_dem = min(min_dem1, min_dem2)
                if based_on_network_peak:
                    new_load = pd.merge(load_profile_f2, network_load, left_index=True, right_index=True)
                    average_peaks_all = np.empty((0, new_load.shape[1] - 1), dtype=float)
                    for m in DemCharCompVal['Month']:
                        new_load2 = new_load.loc[new_load.index.month == m, :].copy()
                        new_load2.sort_values(by='NetworkLoad', inplace=True, ascending=False)
                        average_peaks_all = np.append(average_peaks_all,
                                                      [2 * new_load2.iloc[:num_of_peaks, :-1].values.mean(axis=0)],
                                                      axis=0)
                    average_peaks_all = np.clip(average_peaks_all, a_min=min_dem, a_max=None)
                    average_peaks_all_sum = average_peaks_all.sum(axis=0)
                else:
                    average_peaks_all = np.empty((0, load_profile_f.shape[1]), dtype=float)
                    for m in DemCharCompVal['Month']:
                        arr = load_profile_f.loc[load_profile_f.index.month == m, :].copy().values
                        arr.sort(axis=0)
                        arr = arr[::-1]
                        average_peaks_all = np.append(average_peaks_all, [2 * arr[:num_of_peaks, :].mean(axis=0)],
                                                      axis=0)
                    average_peaks_all = np.clip(average_peaks_all, a_min=min_dem, a_max=None)
                    average_peaks_all_sum = average_peaks_all.sum(axis=0)
                results[TarComp]['Avg_kW_' + DemCharComp] = average_peaks_all_sum / len(DemCharCompVal['Month'])
                results[TarComp]['C_' + DemCharComp] = average_peaks_all_sum * DemCharCompVal['Value']
                results[TarComp]['Charge_Demand'] = results[TarComp][
                    [col for col in results[TarComp] if col.startswith('C_')]].sum(axis=1)

    for k, v in results.items():
        if k != 'LoadInfo':
            results[k]['Bill'] = results[k][[col for col in results[k].columns if col.startswith('Charge')]].sum(axis=1)
    energy_comp_list = ['BlockAnnual', 'BlockQuarterly', 'BlockMonthly', 'BlockDaily', 'FlatRate', 'TOU']
    tariff_comp_list = []
    for TarComp, TarCompVal in tariff['Parameters'].items():
        for TarComp2, TarCompVal2 in tariff['Parameters'][TarComp].items():
            tariff_comp_list.append(TarComp2)
    tariff_comp_list = list(set(tariff_comp_list))
    energy_lst = [value for value in tariff_comp_list if value in energy_comp_list]

    if len(energy_lst) < 1:
        raise ValueError("There is no energy charge component. Please fix the tariff and try again!")
    elif len(energy_lst) > 1:
        raise ValueError( "There are more than one energy charge component. Please fix the tariff and try again!")
    else:
        return results