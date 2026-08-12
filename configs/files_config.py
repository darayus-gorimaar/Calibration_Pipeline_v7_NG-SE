'''File to avoid annoying renaming of discrepant files like "districts.asc" vs "district.asc" in the pipeline'''

from country_config import *

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
observed_initial_population_file = f"{country_code}_initpopulation_{initial_year}.asc"