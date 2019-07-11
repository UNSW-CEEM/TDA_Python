import numpy as np
import pandas as pd
import time
import sys

# Inputs: Tariff and Load profile (30 min interval, one year,
# timestamps are the end of time period: 12:30 is consumption from 12 to 12:30)

def bill_calculator(load_profile, tariff):

    def pre_processing_load(load_profile):

        # placeholder for a quick quality check function for load profile
        # make sure it is kwh
        # make sure it is one year
        # make sure it doesn't have missing value or changing the missing values to zero or to average
        # make sure the name is Load
        # time interval is half hour

        return load_profile

    def fr_calc(load_profile, tariff):

        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']

        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])

        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'Datetime']

        if tariff['ProviderType'] == 'Retailer':
            Results['DailyCharge'] = (len(load_profile.index.normalize().unique())-1) * tariff['Parameters']['Daily']['Value']
            Results['EnergyCharge'] = Results['Annual_kWh'] * tariff['Parameters']['Energy']['Value']
            Results['EnergyCharge_Discounted'] = Results['EnergyCharge'] * (1 - tariff['Discount (%)'] / 100)
            Results['Fit_Rebate'] = Results['Annual_kWh_exp'] * tariff['Parameters']['FiT']['Value']
            Results['Bill'] = Results['DailyCharge'] + Results['EnergyCharge'] - Results['Fit_Rebate']
        else:
            for TarComp, TarCompVal in tariff['Parameters'].items():
                Results[TarComp + '_DailyCharge'] = (len(load_profile.index.normalize().unique())-1) * TarCompVal['Daily']['Value']
                Results[TarComp + '_EnergyCharge'] = Results['Annual_kWh'] * TarCompVal['Energy']['Value']
            Results['Bill'] = Results['NUOS_DailyCharge'] + Results['NUOS_EnergyCharge']
        return Results

    def block_annual(load_profile, tariff):

        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])
        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'Datetime']
        if tariff['ProviderType'] == 'Retailer':
            tariff_temp = tariff.copy()
            del tariff_temp['Parameters']
            tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
            tariff = tariff_temp.copy()


        for TarComp, TarCompVal in tariff['Parameters'].items():
            Results[TarComp + '_DailyCharge'] = (len(load_profile.index.normalize().unique())-1) * TarCompVal['Daily'][
                'Value']
            BlockUse = Results[['Annual_kWh']].copy()
            BlockUseCharge = Results[['Annual_kWh']].copy()

            lim = 0
            for k, v in TarCompVal['Energy'].items():
                BlockUse[k] = BlockUse['Annual_kWh']
                BlockUse[k][BlockUse[k] > v['HighBound']] = v['HighBound']
                BlockUse[k] = BlockUse[k]-lim
                BlockUse[k][BlockUse[k] < 0] = 0
                lim = v['HighBound']
                BlockUseCharge[k] = BlockUse[k] * v['Value']
            del BlockUse['Annual_kWh']
            del BlockUseCharge['Annual_kWh']
            Results[TarComp + '_EnergyCharge'] = BlockUseCharge.sum(axis=1)
            if 'Discount (%)' in tariff:
                Results[TarComp + '_EnergyCharge_Discounted'] = Results[TarComp + '_EnergyCharge'] * (
                            1 - tariff['Discount (%)'] / 100)
            else:
                Results[TarComp + '_EnergyCharge_Discounted'] = Results[TarComp + '_EnergyCharge']
            if 'FiT' in TarCompVal:
                Results[TarComp + '_Fit_Rebate'] = Results['Annual_kWh_exp'] * TarCompVal['FiT']['Value']
            else:
                Results[TarComp + '_Fit_Rebate'] = 0
        if tariff['ProviderType'] == 'Retailer':
            Results['Bill'] = Results['Retailer_DailyCharge'] + Results['Retailer_EnergyCharge_Discounted'] - \
                              Results['Retailer_Fit_Rebate']
        else:
            Results['Bill'] = Results['NUOS_DailyCharge'] + Results['NUOS_EnergyCharge_Discounted'] - Results[
                'NUOS_Fit_Rebate']

        return Results

    def block_quarterly(load_profile, tariff):

        load_profile_imp=load_profile.clip_lower(0)
        load_profile_Q1 = load_profile_imp.loc[load_profile_imp.index.month.isin([1, 2, 3]), :]
        load_profile_Q2 = load_profile_imp.loc[load_profile_imp.index.month.isin([4, 5, 6]), :]
        load_profile_Q3 = load_profile_imp.loc[load_profile_imp.index.month.isin([7, 8, 9]), :]
        load_profile_Q4 = load_profile_imp.loc[load_profile_imp.index.month.isin([10, 11, 12]), :]
        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])
        Results['Q1_kWh'] = load_profile_Q1.sum()
        Results['Q2_kWh'] = load_profile_Q2.sum()
        Results['Q3_kWh'] = load_profile_Q3.sum()
        Results['Q4_kWh'] = load_profile_Q4.sum()
        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'Datetime']
        if tariff['ProviderType'] == 'Retailer':
            tariff_temp = tariff.copy()
            del tariff_temp['Parameters']
            tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
            tariff = tariff_temp.copy()
        for TarComp, TarCompVal in tariff['Parameters'].items():
            Results[TarComp + '_DailyCharge'] = (len(load_profile.index.normalize().unique())-1) * TarCompVal['Daily'][
                'Value']
            for i in range(1,5):
                BlockUse = Results[['Q{}_kWh'.format(i)]].copy()
                BlockUseCharge = BlockUse.copy()
                lim = 0
                for k, v in TarCompVal['Energy'].items():
                    BlockUse[k] = BlockUse['Q{}_kWh'.format(i)]
                    BlockUse[k][BlockUse[k] > v['HighBound']] = v['HighBound']
                    BlockUse[k] = BlockUse[k] - lim
                    BlockUse[k][BlockUse[k] < 0] = 0
                    lim = v['HighBound']
                    BlockUseCharge[k] = BlockUse[k] * v['Value']
                del BlockUse['Q{}_kWh'.format(i)]
                del BlockUseCharge['Q{}_kWh'.format(i)]

                Results[TarComp + '_EnergyCharge_Q{}'.format(i)] = BlockUseCharge.sum(axis=1)
            Results[TarComp + '_EnergyCharge'] = Results[TarComp + '_EnergyCharge_Q1'] +Results[TarComp + '_EnergyCharge_Q2']\
                                               +Results[TarComp + '_EnergyCharge_Q3']+Results[TarComp + '_EnergyCharge_Q4']
            if 'Discount (%)' in tariff:
                Results[TarComp + '_EnergyCharge_Discounted'] = Results[TarComp + '_EnergyCharge'] * (
                        1 - tariff['Discount (%)'] / 100)
            else:
                Results[TarComp + '_EnergyCharge_Discounted'] = Results[TarComp + '_vEnergyCharge']
            if 'FiT' in TarCompVal:
                Results[TarComp + '_Fit_Rebate'] = Results['Annual_kWh_exp'] * TarCompVal['FiT']['Value']
            else:
                Results[TarComp + '_Fit_Rebate'] = 0
        if tariff['ProviderType'] == 'Retailer':
            Results['Bill'] = Results['Retailer_DailyCharge'] + Results['Retailer_EnergyCharge_Discounted'] - \
                              Results['Retailer_Fit_Rebate']
        else:
            Results['Bill'] = Results['NUOS_DailyCharge'] + Results['NUOS_EnergyCharge_Discounted'] - Results[
                'NUOS_Fit_Rebate']
        return Results
    def tou_calc(load_profile, tariff):
        t0 = time.time()
        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']

        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])

        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'Datetime']
        if tariff['ProviderType'] == 'Retailer':
            tariff_temp = tariff.copy()
            del tariff_temp['Parameters']
            tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
            tariff = tariff_temp.copy()
        for TarComp, TarCompVal in tariff['Parameters'].items():
            Results[TarComp + '_DailyCharge'] = (len(load_profile.index.normalize().unique())-1) * TarCompVal['Daily']['Value']
            time_ind = np.zeros(load_profile.shape[0])
            load_profile_TI = pd.DataFrame()
            load_profile_TI_Charge = pd.DataFrame()
            ti = 0
            for k, v in TarCompVal['Energy'].items():
                this_part = v.copy()
                ti += 1
                for k2, v2, in this_part['TimeIntervals'].items():
                    start_hour = int(v2[0][0:2])
                    if start_hour == 24:
                        start_hour = 0
                    start_min = int(v2[0][3:5])
                    end_hour = int(v2[1][0:2])
                    if end_hour == 0:
                        end_hour = 24
                    end_min = int(v2[1][3:5])
                    if this_part['Weekday']:
                        if start_hour <= end_hour:
                            time_ind = np.where((load_profile.index.weekday < 5) &
                                                (load_profile.index.month.isin(this_part['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  > (60 * start_hour + start_min)) &
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  <= (60 * end_hour + end_min))), ti,
                                                time_ind)
                        else:
                            time_ind = np.where((load_profile.index.weekday < 5) &
                                                                (load_profile.index.month.isin(this_part['Month'])) &
                                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  > (60 * start_hour + start_min)) |
                                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  <= (60 * end_hour + end_min))), ti,
                                                                time_ind)
                    if this_part['Weekend']:
                        if start_hour <= end_hour:
                            time_ind = np.where((load_profile.index.weekday >= 5) &
                                                                (load_profile.index.month.isin(this_part['Month'])) &
                                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  > (60 * start_hour + start_min)) &
                                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  <= (60 * end_hour + end_min))), ti,
                                                                time_ind)
                        else:
                            time_ind = np.where((load_profile.index.weekday >= 5) &
                                                                (load_profile.index.month.isin(this_part['Month'])) &
                                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  > (60 * start_hour + start_min)) |
                                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  <= (60 * end_hour + end_min))), ti,
                                                                time_ind)
                load_profile_TI[k] = load_profile.loc[time_ind == ti, :].sum()
                load_profile_TI_Charge[k] = this_part['Value'] * load_profile_TI[k]
            Results[TarComp + '_EnergyCharge'] = load_profile_TI_Charge.sum(axis=1)
            if 'Discount (%)' in tariff:
                Results[TarComp + '_EnergyCharge_Discounted'] = Results[TarComp + '_EnergyCharge'] * (1 - tariff['Discount (%)'] / 100)
            else:
                Results[TarComp + '_EnergyCharge_Discounted'] = Results[TarComp + '_EnergyCharge']
            if 'FiT' in TarCompVal:
                Results[TarComp + '_Fit_Rebate'] = Results['Annual_kWh_exp'] * TarCompVal['FiT']['Value']
            else:
                Results[TarComp + '_Fit_Rebate'] = 0
        if tariff['ProviderType'] == 'Retailer':
            Results['Bill'] = Results['Retailer_DailyCharge'] + Results['Retailer_EnergyCharge_Discounted'] - Results['Retailer_Fit_Rebate']
        else:
            Results['Bill'] = Results['NUOS_DailyCharge'] + Results['NUOS_EnergyCharge_Discounted'] - Results['NUOS_Fit_Rebate']

        print(time.time() - t0)

        return Results

    def demand_charge(load_profile, tariff):

        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])

        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'Datetime']

        if tariff['ProviderType'] == 'Retailer':
            tariff_temp = tariff.copy()
            del tariff_temp['Parameters']
            tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
            tariff = tariff_temp.copy()
        for TarComp, TarCompVal in tariff['Parameters'].items():
            Results[TarComp + '_DailyCharge'] = (len(load_profile.index.normalize().unique())-1) * TarCompVal['Daily'][
                'Value']
            if ('Unit', '$/kWh') in TarCompVal['Energy'].items():
                Results[TarComp + '_EnergyCharge'] = Results['Annual_kWh'] * TarCompVal['Energy']['Value']
            else:
                load_profile_imp = load_profile.clip_lower(0)
                load_profile_Q1 = load_profile_imp.loc[load_profile_imp.index.month.isin([1, 2, 3]), :]
                load_profile_Q2 = load_profile_imp.loc[load_profile_imp.index.month.isin([4, 5, 6]), :]
                load_profile_Q3 = load_profile_imp.loc[load_profile_imp.index.month.isin([7, 8, 9]), :]
                load_profile_Q4 = load_profile_imp.loc[load_profile_imp.index.month.isin([10, 11, 12]), :]
                Results['Q1_kWh'] = load_profile_Q1.sum()
                Results['Q2_kWh'] = load_profile_Q2.sum()
                Results['Q3_kWh'] = load_profile_Q3.sum()
                Results['Q4_kWh'] = load_profile_Q4.sum()
                for i in range(1, 5):
                    BlockUse = Results[['Q{}_kWh'.format(i)]].copy()
                    BlockUseCharge = BlockUse.copy()
                    lim = 0
                    for k, v in TarCompVal['Energy'].items():
                        BlockUse[k] = BlockUse['Q{}_kWh'.format(i)]
                        BlockUse[k][BlockUse[k] > v['HighBound']] = v['HighBound']
                        BlockUse[k] = BlockUse[k] - lim
                        BlockUse[k][BlockUse[k] < 0] = 0
                        lim = v['HighBound']
                        BlockUseCharge[k] = BlockUse[k] * v['Value']
                    del BlockUse['Q{}_kWh'.format(i)]
                    del BlockUseCharge['Q{}_kWh'.format(i)]
                    Results[TarComp + '_EnergyCharge_Q{}'.format(i)] = BlockUseCharge.sum(axis=1)
                Results[TarComp + '_EnergyCharge'] = Results[TarComp + '_EnergyCharge_Q1'] + Results[TarComp + '_EnergyCharge_Q2'] \
                                                   + Results[TarComp + '_EnergyCharge_Q3'] + Results[
                                                       TarComp + '_EnergyCharge_Q4']
            if 'Discount (%)' in tariff:
                Results[TarComp + '_EnergyCharge_Discounted'] = Results[TarComp + '_EnergyCharge'] * (
                        1 - tariff['Discount (%)'] / 100)
            else:
                Results[TarComp + '_EnergyCharge_Discounted'] = Results[TarComp + '_EnergyCharge']
            if 'FiT' in TarCompVal:
                Results[TarComp + '_Fit_Rebate'] = Results['Annual_kWh_exp'] * TarCompVal['FiT']['Value']
            else:
                Results[TarComp + '_Fit_Rebate'] = 0
            # Results[TarComp + '_Demand'] = 0
            Results[TarComp + '_DemandCharge'] = 0
            for DemCharComp, DemCharCompVal in TarCompVal['Demand'].items():

                TSNum = DemCharCompVal['Demand Window Length']   # number of timestamp
                NumofPeaks = DemCharCompVal['Number of Peaks']


                if TSNum > 1:
                    load_profile_r = load_profile.rolling(TSNum, min_periods=1).mean()
                else:
                    load_profile_r = load_profile
                time_ind = np.zeros(load_profile.shape[0])
                ti = 1

                for k2, v2, in DemCharCompVal['TimeIntervals'].items():
                    start_hour = int(v2[0][0:2])
                    if start_hour == 24:
                        start_hour = 0
                    start_min = int(v2[0][3:5])
                    end_hour = int(v2[1][0:2])
                    if end_hour == 0:
                        end_hour = 24
                    end_min = int(v2[1][3:5])
                    if DemCharCompVal['Weekday']:
                        if start_hour <= end_hour:
                            time_ind = np.where((load_profile.index.weekday < 5) &
                                                (load_profile.index.month.isin(DemCharCompVal['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  > (60 * start_hour + start_min)) &
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  <= (60 * end_hour + end_min))), ti,
                                                time_ind)
                        else:
                            time_ind = np.where((load_profile.index.weekday < 5) &
                                                (load_profile.index.month.isin(DemCharCompVal['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  > (60 * start_hour + start_min)) |
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  <= (60 * end_hour + end_min))), ti,
                                                time_ind)
                    if DemCharCompVal['Weekend']:
                        if start_hour <= end_hour:
                            time_ind = np.where((load_profile.index.weekday >= 5) &
                                                (load_profile.index.month.isin(DemCharCompVal['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  > (60 * start_hour + start_min)) &
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  <= (60 * end_hour + end_min))), ti,
                                                time_ind)
                        else:
                            time_ind = np.where((load_profile.index.weekday >= 5) &
                                                (load_profile.index.month.isin(DemCharCompVal['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  > (60 * start_hour + start_min)) |
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  <= (60 * end_hour + end_min))), ti,
                                                time_ind)

                load_profile_r = load_profile_r.loc[time_ind == ti, :]
                load_profile_f = load_profile_r.copy()
                load_profile_f = load_profile_f.reset_index()

                load_profile_f = pd.melt(load_profile_f, id_vars=['Datetime'],
                                         value_vars=[x for x in load_profile_f.columns if x != 'Datetime'])
                load_profile_f = load_profile_f.rename(columns={'variable': 'HomeID', 'value': 'kWh'})

                load_profile_f['Month'] = pd.to_datetime(load_profile_f['Datetime']).dt.month

                if 'Capacity' in DemCharCompVal:
                    capacity = DemCharCompVal['Capacity']['Value']
                    if 'Capacity Exceeded No' in DemCharCompVal:
                        cap_exc_no = DemCharCompVal['Capacity Exceeded No']
                    else:
                        cap_exc_no = 0

                    load_profile_f['kWh'] = load_profile_f['kWh']-(capacity / 2)
                    load_profile_f['kWh'] = load_profile_f['kWh'].clip_lower(0)

                    # load_profile_f.loc[:, 'kWh'][load_profile_f['kWh'] < capacity / 2] = 0
                    load_profile_f['Flag'] = 0
                    load_profile_f.loc[:, 'Flag'][load_profile_f['kWh'] > 0] = 1
                    load_profile_f.groupby(['HomeID', 'Month'])
                    temp2 = load_profile_f.groupby(['HomeID', 'Month', load_profile_f['Datetime'].dt.normalize()]).sum().reset_index()
                    temp2['Flag'] = temp2['Flag'].clip_upper(1)
                    temp3 = temp2.groupby(['HomeID', 'Month']).sum().reset_index()
                    temp3.loc[:, 'Flag'][temp3['Flag'] <= cap_exc_no] = 0
                    temp3.loc[:, 'Flag'][temp3['Flag'] > cap_exc_no] = 1
                    load_profile_f2 = load_profile_f[['Datetime', 'HomeID', 'Month', 'kWh']].merge(temp3[['HomeID', 'Month', 'Flag']], left_on=['HomeID', 'Month'], right_on=['HomeID', 'Month'])
                    load_profile_f2.loc[:, 'kWh'][load_profile_f2['Flag'] < 1] = 0
                else:
                    load_profile_f2=load_profile_f.copy()

                average_peaks = 2 * load_profile_f2[['HomeID', 'kWh', 'Month']].groupby(['HomeID', 'Month']).apply(
                    lambda x: x.sort_values('kWh', ascending=False)[:NumofPeaks]).reset_index(drop=True).groupby(
                    ['HomeID']).mean()
                # Results[TarComp + '_Demand'] = Results[TarComp + '_Demand'] + average_peaks['kWh']
                Results[TarComp + '_DemandCharge'] = Results[TarComp + '_DemandCharge'] + average_peaks['kWh'] * DemCharCompVal['Value'] * len(DemCharCompVal['Month'])
                # AllAveragePeaks = AllAveragePeaks.append(average_peaks)

        if tariff['ProviderType'] == 'Retailer':

            Results['Bill'] = Results['Retailer_DailyCharge'] + Results['Retailer_EnergyCharge_Discounted'] + \
                              Results['Retailer_DemandCharge'] - Results['Retailer_Fit_Rebate']
        else:
            Results['Bill'] = Results['NUOS_DailyCharge'] + Results['NUOS_EnergyCharge_Discounted'] + \
                              Results['NUOS_DemandCharge'] - Results['NUOS_Fit_Rebate']
        return Results



    # Checking the type and run the appropriate function
    load_profile = pre_processing_load(load_profile)
    if tariff['Type'] == 'Flat_rate':
        Results = fr_calc(load_profile, tariff)
    elif tariff['Type'] == 'TOU':
        Results = tou_calc(load_profile, tariff)
    elif tariff['Type'] == 'Block_Annual':
        Results = block_annual(load_profile, tariff)
    elif tariff['Type'] == 'Block_Quarterly':
        Results = block_quarterly(load_profile, tariff)
    elif tariff['Type'] == 'Demand Charge':
        Results = demand_charge(load_profile, tariff)
    else:
        Results = 'Error'
    return Results

