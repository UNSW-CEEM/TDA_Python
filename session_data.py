
class ProjectData():
    def __init__(self):
        self.name = ''

        # Results from calculating bill for a set of load profiles with a given tariff. Stored on a case name basis.
        self.network_results_by_case = {}
        self.retail_results_by_case = {}
        self.wholesale_results_by_case = {}

        # Tariff for a given case, stored on a case name basis.
        self.network_tariffs_by_case = {}
        self.retail_tariffs_by_case = {}

        # The source file name which describes were the load data came from for a given case, stored on a case name
        # basis.
        self.load_file_name_by_case = {}

        # Number of users for a given case.
        self.load_n_users_by_case = {}

        # The filtering used for a given case, stored on a case name basis.
        self.filter_options_by_case = {}

        # Demographic info of load profiles used.
        self.demographic_info_by_case = {}

        # Wholesale price info
        self.wholesale_price_info_by_case = {}

        # Add original data that cannot be deleted (this allows for us to restore to original load data)
        self.original_data = [
            'SampleLoad_without_demo',
            'test_data',
        ]


class InMemoryData:
    def __init__(self):
        # Dictionaries for storing data associated with the current state of the program.

        self.raw_data = {}  # Data as loaded from feather files, stored in dict on a file name basis

        # 1) raw data is filtered by percentage of allowed missing data
        self.filter_missing_data = None

        # 2) filter_missing_data is downsampled by user defined percentage
        self.downsample_data = None

        # 3) downsample_data is filtered by demographic
        self.filtered_data = None
        self.is_filtered = False  # Flag to indicate if filtering has been applied

        # 4) filtered_data is used to calculate user load profiles after end-user-tech (solar/battery/demand response)
        self.end_user_tech_data = None

        self.raw_data_name = None
        # Chart data for the load plots, only storing data for non filtered data as filtering can change between plot
        # updates.
        # Stored on a file name basis.
        self.raw_charts = {}

        # Load profiles after any filtering, for a given case, stored on a case name basis.
        self.load_by_case = {}

        # Current demographic info after filter.
        self.filtered_demo_info = None

        # End user technology sample.
        self.end_user_tech_sample = None
        self.end_user_tech_sample_applied = False

        # Filtering options applied to get the current filtered data.
        self.filter_state = None

        self.solar_profile_data = {} # Data as loaded from feather files, stored in dict on a file name basis

        self.network_load = None

        # Data subset to save/load.
        self.project_data = ProjectData()
