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


def add_to_load_2_demo_map(file_name):
    load_2_demo_map = pd.read_csv('data/load_2_demo_map.csv')
    new_load_2_demo_map = load_2_demo_map.copy()
    mapped_files = new_load_2_demo_map['load'].tolist()

    if file_name not in mapped_files:
        new_load_2_demo_map = new_load_2_demo_map.append(
            pd.DataFrame({'load': [file_name], 'demo': ['demo_' + file_name]}))

    new_load_2_demo_map.to_csv('data/load_2_demo_map.csv', index=False)


def load_data_to_dataframe(file_path):
    base = os.path.basename(file_path)
    path_extension = os.path.splitext(base)[1]

    if path_extension == '.csv':
        load_data = pd.read_csv(file_path)
        demo_data = pd.DataFrame({'CUSTOMER_KEY': []})
    else:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        if len(sheet_names) >= 2:  # check to see if excel sheet contains two sheets, one for load data and one for demo data.
            load_data = pd.read_excel(xls, sheet_names[0])
            demo_data = pd.read_excel(xls, sheet_names[1])
            if demo_data.empty == True:
                import_demo_data = pd.DataFrame({'CUSTOMER_KEY': []})
        elif len(sheet_names) == 1:  # allow user to upload only load data without demo data.
            load_data = pd.read_excel(xls, sheet_names[0])
            demo_data = pd.DataFrame({'CUSTOMER_KEY': []})

    return load_data, demo_data


def generic_data_to_dataframe(file_path):
    base = os.path.basename(file_path)
    path_extension = os.path.splitext(base)[1]

    if path_extension == '.csv':
        data = pd.read_csv(file_path)
    else:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        data = pd.read_excel(xls, sheet_names[0])

    return data


def check_data_is_not_default(file_name, list_of_default_data):
    # this function checks whether the file that is being selected is the default/original data or not
    # Used as check to prevent deleting default data
    if file_name not in list_of_default_data:
        return True
    else:
        return False


def check_load_2_demo_map():
    # Fix load_2_demo_map if corrupted or not mapping available data from database
    load_2_demo_map = pd.read_csv('data/load_2_demo_map.csv')
    new_load_2_demo_map = load_2_demo_map.copy()

    ###############################
    # check that load_2_demo_map has valid columns
    default_columns = ['load', 'demo']
    columns = new_load_2_demo_map.columns.tolist()
    if columns == default_columns:
        pass
    else:
        new_load_2_demo_map.columns = default_columns

    ###############################
    # Get list of all files in database:
    load_database_files = os.listdir('data/load/')
    demo_database_files = os.listdir('data/demographics/')


    list_valid_files_in_database = []
    for file in demo_database_files:
        if file.lstrip('demo_') in load_database_files:
            file_name = os.path.splitext(file.lstrip('demo_'))[0]
            list_valid_files_in_database.append(file_name)

    ###############################
    # check that load_2_demo_map is mapping files that exists
    # if mapped files does not exist, delete from csv file

    list_valid_mapped_files = []
    for index, files in new_load_2_demo_map.iterrows():
        load_file_exist = check_file_exists('data/load/' + files[0] + '.feather')
        demo_file_exist = check_file_exists('data/demographics/' + 'demo_' + files[0] + '.feather')
        if load_file_exist == True & demo_file_exist == True:
            list_valid_mapped_files.append(files[0])
            pass
        else:
            new_load_2_demo_map = new_load_2_demo_map.drop(index, axis=0)

    new_load_2_demo_map.to_csv('data/load_2_demo_map.csv', index=False)

    ###############################
    # check if valid files in database has been mapped in load_2_demo_map
    # if files in database has not been mapped, mapped it in load_2_demo_map
    for file in list_valid_files_in_database:
        if file not in list_valid_mapped_files:
            add_to_load_2_demo_map(file)















