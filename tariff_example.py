import TariffDraft
import pandas as pd

time_stamps = ['2017/01/01 00:30:00', '2017/01/01 01:00:00', '2017/01/01 01:30:00', '2017/01/01 02:00:00']
load = [1, 1, 1, 1]
load_df = pd.DataFrame({'TimeStamp': time_stamps, 'Energy': load})
load_df['TimeStamp'] = pd.to_datetime(load_df['TimeStamp'])

tariff_parameters = [[TariffDraft.BlockCharge, 0.5]]

myTariff = TariffDraft.Tariff(tariff_parameters)

bill = myTariff.bill(load_df)

more_complicated_parameters = [[TariffDraft.BlockCharge, 0.5, 0, 2],
                               [TariffDraft.BlockCharge, 1, 2, 4]]

complicatedTariff = TariffDraft.Tariff(more_complicated_parameters)

bill2 = complicatedTariff.bill(load_df)

x=1

