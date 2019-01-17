import pandas as pd
import feather
import time

load = pd.read_csv('data/'+'General_filtered.csv')
feather.write_dataframe(load, 'data/'+'General_filtered.feather')

t0 = time.time()
load = feather.read_dataframe('data/'+'Control_filtered.feather')
print(time.time()-t0)
t0 = time.time()
loads = load.melt(id_vars=['READING_DATETIME'], var_name='ID', value_name='power')
loads = loads.set_index('READING_DATETIME')
loadv = loads.power
print(time.time()-t0)
t0 = time.time()
agg_load = loads.groupby(['READING_DATETIME', 'ID']).sum()
print('groupby {}'.format(time.time()-t0))
t0 = time.time()
agg_load = loads.groupby('READING_DATETIME').mean()
print(time.time()-t0)
t0 = time.time()
load['mean'] = load.mean(axis=1)
print(time.time()-t0)
