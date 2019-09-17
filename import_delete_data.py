import os
import pandas as pd

def check_valid_filetype(file_path, allowed_extensions):
    # allowed_extensions should be in the following format: {".csv", ".xls", ".xlsx"}
    base = os.path.basename(file_path)
    path_extension = os.path.splitext(base)[1]

    if path_extension in allowed_extensions:
        return True
    else:
        return False


def check_file_exists(file_path):

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return True
    else:
        return False

def fix_load_2_demo_map():
    load_2_demo_map = pd.read_csv('data/load_2_demo_map.csv')
    new_load_2_demo_map = load_2_demo_map.copy()

    # check if csv contains the correct headers:
    default_columns = ['load', 'demo']
    columns = new_load_2_demo_map.columns.tolist()

    # check that load_2_demo_map has valid columns
    if columns == default_columns:
        pass
    else:
        new_load_2_demo_map.columns = default_columns

    # check that load_2_demo_map is mapping files that exists
    # if mapped files does not exist, delete from csv file
    for index, files in new_load_2_demo_map.iterrows():
        load_file_exist = check_file_exists('data/load/' + files[0] + '.feather')
        demo_file_exist = check_file_exists('data/demographics/' + files[0] + '.feather')
        if load_file_exist == True & demo_file_exist == True:
            pass
        else:
            new_load_2_demo_map = new_load_2_demo_map.drop(index, axis=0)

    new_load_2_demo_map.to_csv('data/load_2_demo_map.csv', index=False)


def import_load_data():

    pass


def import_network_data():
    pass


def import_solar_data():
    pass


def check_data_is_not_default(file_name, list_of_default_data):
    # this function checks whether the file that is being selected is the default/original data or not
    # Used as check to prevent deleting default data
    if file_name not in list_of_default_data:
        return True
    else:
        return False




















