from _configs.files_config import *

SEASONALLITY_MODE = "one"
NUM_BINS = 5
betas = [0.001, 0.005, 0.01, 0.0125, 0.015, 0.02, 0.03, 0.04, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.1]
# betas = [0.1, 0.5, 1]
calibration_replicates = 25
validation_replicates = 15

# population scales
pre_calibration_sim_scale = 1                           # Full Value: 1
pre_calibration_population_validation_scale = 0.25      # Full Value: 0.25
calibration_population_scale = 0.01                        # Full Value: 1
validation_population_scale = 0.001                      # Full Value: 0.25

###############################################################

run_number = 1 

###############################################################

''' Pre-calibration Paths '''
pre_sim_run_path = f"_pre_sim_200k_pop_run"
PRE_SIM_RUN_PATH_INPUTS_DIR = f"{pre_sim_run_path}/input"
pre_sim_analysis_path = f"{pre_sim_run_path}/analysis"

pre_calibration_run_path = f"_pre_calibration_population_growth_rate_validation"
PRE_CALIBRATION_RUN_INPUTS_DIR = f"{pre_calibration_run_path}/input"
pre_calibration_analysis_path = f"{pre_calibration_run_path}/analysis"

''' Calibration Paths '''
calibration_path = f"calibration_{run_number}_{SEASONALLITY_MODE}_pattern_{calibration_replicates}_replicates"
CALIBRATION_RUN_INPUTS_DIR = f"{calibration_path}/input"
calibration_analysis_path = f"{calibration_path}/analysis"

''' Validation Paths '''
# validation_path = f"validation_test"
# validation_path = f"validation_{run_number}_{validation_population_scale}_population_scale_{SEASONALLITY_MODE}_pattern_{validation_replicates}_replicates"
# validation_path = f"validation_1_copy_zero_beta"
validation_path = f"validation_1_copy_new_treatment_seeking_zero_beta" 
# validation_path = f"validation_{validation_population_scale}_population_scale_{SEASONALLITY_MODE}_pattern_{validation_replicates}_replicates"
VALIDATION_RUN_INPUTS_DIR = f"{validation_path}/input"
log_path = f"{validation_path}/log"
validation_output_path = f"{validation_path}/output"
script_path = f"{validation_path}/script"