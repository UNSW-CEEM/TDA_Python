import numpy as np
import pandas as pd
import time
import sys

# https://github.com/UNSW-CEEM/Bill_Calculator
#
# Inputs: Tariff and Load profile (30 min interval, one year,
# timestamps are the end of time period: 12:30 is consumption from 12 to 12:30)

def bill_calculator(load_profile, tariff, network_load=None, FiT=True):

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
        # Setting the export load to zero (consider only import for now)
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']
        # creating the results dataframe which has all the results
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])
        # if has feed in tariff calculate the export as well
        if FiT:
            Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'Datetime']
        # if retail tariff calculate the daily and energy from the parameters
        if tariff['ProviderType'] == 'Retailer':
            # daily charge using the number of unique days in the load profile
            Results['DailyCharge'] = (len(load_profile.index.normalize().unique())-1) * tariff['Parameters']['Daily']['Value']
            # calculate the energy charge by multiplying the energy by usage
            Results['EnergyCharge'] = Results['Annual_kWh'] * tariff['Parameters']['Energy']['Value']
            #  if there is discount
            Results['EnergyCharge_Discounted'] = Results['EnergyCharge'] * (1 - tariff['Discount (%)'] / 100)
            # if there is feed in tariff add a new column to df with the rebate
            if FiT:
                Results['Fit_Rebate'] = Results['Annual_kWh_exp'] * tariff['Parameters']['FiT']['Value']
            else:
                Results['Fit_Rebate'] = 0
            #     final bill is the sum of daily charge, energy charge and negative rebate of the feed in tariff
            Results['Bill'] = Results['DailyCharge'] + Results['EnergyCharge'] - Results['Fit_Rebate']
        else:
            # if it's network tariff do the same for each component separately
            for TarComp, TarCompVal in tariff['Parameters'].items():
                Results[TarComp + '_DailyCharge'] = (len(load_profile.index.normalize().unique())-1) * TarCompVal['Daily']['Value']
                Results[TarComp + '_EnergyCharge'] = Results['Annual_kWh'] * TarCompVal['Energy']['Value']
            Results['Bill'] = Results['NUOS_DailyCharge'] + Results['NUOS_EnergyCharge']
        return Results
    # block annual tariff where you have different charges for different levels of usage
    def block_annual(load_profile, tariff):
        # The high bounds is for annual
        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])
        if FiT:
            Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'Datetime']
        # if it's retailer change the layout so it's similar to network tariff component
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
            # separating the blocks of usage
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
        # The high bounds is for each quarter (so if you have annual bound you should divide it by four!)
        load_profile_imp = load_profile.clip_lower(0)
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
        if FiT:
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

    def block_monthly(load_profile, tariff):
        # The high bounds is for each month (so if you have annual bound you should divide it by 12!)
        load_profile_imp = load_profile.clip_lower(0)
        load_profile_M={}
        for m in range(1, 13):
            load_profile_M['M_'+str(m)] = load_profile_imp.loc[load_profile_imp.index.month == m, :]


        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])
        for m in range(1, 13):
            Results['M'+str(m)+'_kWh'] = load_profile_M['M_'+str(m)].sum()

        if FiT:
            Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                         for col in f_load_profile.columns if col != 'Datetime']
        if tariff['ProviderType'] == 'Retailer':
            tariff_temp = tariff.copy()
            del tariff_temp['Parameters']
            tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
            tariff = tariff_temp.copy()
        for TarComp, TarCompVal in tariff['Parameters'].items():
            Results[TarComp + '_DailyCharge'] = (len(load_profile.index.normalize().unique()) - 1) * \
                                                TarCompVal['Daily'][
                                                    'Value']
            for m in range(1, 13):
                BlockUse = Results[['M{}_kWh'.format(m)]].copy()
                BlockUseCharge = BlockUse.copy()
                lim = 0
                for k, v in TarCompVal['Energy'].items():
                    BlockUse[k] = BlockUse['M{}_kWh'.format(m)]
                    BlockUse[k][BlockUse[k] > v['HighBound']] = v['HighBound']
                    BlockUse[k] = BlockUse[k] - lim
                    BlockUse[k][BlockUse[k] < 0] = 0
                    lim = v['HighBound']
                    BlockUseCharge[k] = BlockUse[k] * v['Value']
                del BlockUse['M{}_kWh'.format(m)]
                del BlockUseCharge['M{}_kWh'.format(m)]

                Results[TarComp + '_EnergyCharge_M{}'.format(m)] = BlockUseCharge.sum(axis=1)

            Results[TarComp + '_EnergyCharge'] = Results[[TarComp + '_EnergyCharge_M' + str(m) for m in range(1, 13)]].sum(axis=1)
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


    def tou_calc(load_profile, tariff):
        # different charge in different times of day, month, weekday weekend,
        t0 = time.time()
        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']

        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])

        if FiT:
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
                    # todo: adding holiday workday
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
        # charge per kW based on the maximum demand of the month
        f_load_profile = load_profile.copy()
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'Datetime']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'Datetime'],
                               data=imports, columns=['Annual_kWh'])
        if FiT:
            Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'Datetime']
        # if this is a retail tariff create a new item in the parameters and make it retailer to make it similar to network tariffs
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
                Results['Q1_kWh'] = load_profile_imp.loc[load_profile_imp.index.month.isin([1, 2, 3]), :].sum()
                Results['Q2_kWh'] = load_profile_imp.loc[load_profile_imp.index.month.isin([4, 5, 6]), :].sum()
                Results['Q3_kWh'] = load_profile_imp.loc[load_profile_imp.index.month.isin([7, 8, 9]), :].sum()
                Results['Q4_kWh'] = load_profile_imp.loc[load_profile_imp.index.month.isin([10, 11, 12]), :].sum()
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
                    load_profile_r = load_profile.copy()
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

                load_profile_f = load_profile_r.loc[time_ind == ti, :].copy().reset_index()
                load_profile_f = pd.melt(load_profile_f, id_vars=['Datetime'],
                                         value_vars=[x for x in load_profile_f.columns if x != 'Datetime'])
                load_profile_f = load_profile_f.rename(columns={'variable': 'HomeID', 'value': 'kWh'})
                load_profile_f['Month'] = load_profile_f['Datetime'].dt.month
                # if capacity charge is applied meaning the charge only applies when you exceed the capacity for  a certain number of times
                if 'Capacity' in DemCharCompVal:
                    # please note the capacity charge only works with user's demand peak (not coincident peak)
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
                    load_profile_f2 = load_profile_f.copy()

                if DemCharCompVal['Based on Network Peak']:
                    new_load = load_profile_f2.merge(network_load, on='Datetime').rename(columns={0: 'NetworkLoad'})
                    average_peaks = 2 * new_load[['HomeID', 'kWh', 'Month', 'NetworkLoad']].groupby(['HomeID', 'Month']).apply(
                        lambda x: x.sort_values('NetworkLoad', ascending=False)[:NumofPeaks]).reset_index(drop=True).groupby(
                        ['HomeID']).mean()
                else:
                    average_peaks = 2 * load_profile_f2[['HomeID', 'kWh', 'Month']].groupby(['HomeID', 'Month']).apply(
                        lambda x: x.sort_values('kWh', ascending=False)[:NumofPeaks]).reset_index(drop=True).groupby(
                        ['HomeID']).mean()

                Results[TarComp + '_DemandCharge'] = Results[TarComp + '_DemandCharge'] + average_peaks['kWh'] * DemCharCompVal['Value'] * len(DemCharCompVal['Month'])

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
    elif tariff['Type'] == 'Block_Monthly':
        Results = block_monthly(load_profile, tariff)
    elif tariff['Type'] == 'Demand Charge':
        Results = demand_charge(load_profile, tariff)
    else:
        Results = 'Error'
    return Results

