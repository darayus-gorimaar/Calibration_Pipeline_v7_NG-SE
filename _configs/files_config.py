'''File to avoid annoying renaming of discrepant files like "districts.asc" vs "district.asc" in the pipeline'''

from _configs.country_config import *

############################## Data files ##############################

''' Edit before running pipeline '''
########################################################################
pfpr_file_name = f"{country_code}_pfpr_{calibration_year}.asc"    
# pfpr_file_name = f"{country_code}_pfpr2to10_{calibration_year}.asc" 

district_raw_file_name = f"{country_code}_district.asc"  
district_raw_file_name = f"{country_code}_district.asc"  

treatment_seeking_file_name = f"{country_code}_treatment_seeking_normalized.asc" 
########################################################################

''' Edit after running Notebook 0_1 '''
########################################################################
district_file_name_sequential = f"district_sequence_1.asc" 

# input_population_file = f"{country_code}_initpopulation_{initial_year}_20.6M.asc"
input_population_file = f"{country_code}_initpopulation_{initial_year}_inferred_for_sim.asc"


########################################################################
''' ALL THE FILES I NEED TO NAME AND ORGANIZE '''
########################################################################

# /DATA/ 
observed_population_raster_path = f"{data_path}/{country_code}_population_{observed_population_year}_world_pop_data.asc"
districts_raster_path = f"{data_path}/{country_code}_district.asc"

#/generated/
projected_population_calibration_year_raster_path = f"{generated_data_path}/{country_code}_population_projected_{calibration_year}.asc"


population_per_district_projected_csv_path = f"{generated_data_path}/population_per_district_projected_{calibration_year}.csv"