'''File to avoid annoying renaming of discrepant files like "districts.asc" vs "district.asc" in the pipeline'''

from _configs.country_config import *

############################## Data files ##############################

''' Edit before running pipeline '''
########################################################################
pfpr_file_name = f"{country_code}_pfpr_{calibration_year}.asc"    
# pfpr_file_name = f"{country_code}_pfpr2to10_{calibration_year}.asc" 

district_raw_file_name = f"{country_code}_district.asc"  
district_raw_file_name = f"{country_code}_district.asc"  


########################################################################

''' Edit after running Notebook 0_1 '''
########################################################################
district_file_name_sequential = f"district_sequence_1.asc" 

# input_population_file = f"{country_code}_initpopulation_{initial_year}_20.6M.asc"


########################################################################
''' ALL THE FILES I NEED TO NAME AND ORGANIZE '''
########################################################################

# /DATA/ 
observed_population_raster_path = f"{data_path}/{country_code}_population_{observed_population_year}_world_pop_data.asc"
districts_raster_path = f"{data_path}/{country_code}_district.asc"
districts_raster_sequential_path = f"{data_path}/{country_code}_district_seq1.asc"
treatment_seeking_raster_path = f"{data_path}/{country_code}_treatment_seeking_normalized.asc" 
travel_time_raster_path = f"{data_path}/{country_code}_traveltime.asc"

incidence_data_csv_path = f"{data_path}/Incidence Data/{country_code}_incidence_data_for_pipeline_DO_NOT_MODIFY.csv"

#/generated/
initial_population_projected_raster_path = f"{generated_data_path}/{country_code}_population_backwards_projected_{initial_year}.asc"
projected_population_calibration_year_raster_path = f"{generated_data_path}/{country_code}_population_projected_{calibration_year}.asc"

zero_beta_raster_path = f"{generated_data_path}/{country_code}_beta_zero.asc"


population_per_district_projected_csv_path = f"{generated_data_path}/population_per_district_projected_{calibration_year}.csv"

population_incidence_per_district_csv_path = f"{generated_data_path}/population_incidence_per_district.csv"


# Templates
BETA_RASTER_TEMPLATE = f"{template_path}/{country_code}_beta.template"
ACCESS_RASTER_TEMPLATE = f"{template_path}/{country_code}_treatmentseeking.template"
POPULATION_BIN_RASTER_TEMPLATE = f"{template_path}/{country_code}_initialpopulation_1_location.template"


