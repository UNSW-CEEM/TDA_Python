import pandas as pd
import feather
from import_delete_data import check_valid_filetype, check_file_exists, check_load_2_demo_map, check_data_is_not_default, \
    add_to_load_2_demo_map, load_data_to_dataframe, generic_data_to_dataframe


# file_name = 'SGSC2013'

# read file and load into dataframe

# load_data, demo_data = load_data_to_dataframe('data2/Load Profiles/AG300_G_2010.xlsx')

# demo_data = pd.read_csv('data2/Load Profiles/SGSC2013_info.csv')

# demo_data = demo_data.drop(demo_data.columns[0], axis=1)


# load_data[load_data.columns[0]] = pd.to_datetime(load_data[load_data.columns[0]])
# load_data.rename(columns={load_data.columns[0]: 'Datetime'}, inplace=True)
# demo_data.rename(columns={demo_data.columns[0]: 'CUSTOMER_KEY'}, inplace=True)

# print(demo_data)

# Add mapping of imported file into load_2_demo_map.csv
# add_to_load_2_demo_map(file_name)

# Add import load files to database


# feather.write_dataframe(load_data, 'data/load/' + file_name + '.feather')
# feather.write_dataframe(demo_data, 'data/demographics/' + 'demo_' + file_name + '.feather')
