# %%
from pathlib import Path
import numpy as np
import os
import pandas as pd
import yaml

from _configs.country_config import *
from _configs.files_config import *
from _configs.run_config import *

from _utils.utils import *

# %%
input_data = yaml.safe_load((Path(VALIDATION_RUN_INPUTS_DIR)/"input_validation.yml").read_text(encoding="utf-8"))

population_scale_from_input_yml = input_data["population_demographic"]["artificial_rescaling_of_population_size"]
starting_date = input_data["simulation_timeframe"]["starting_date"]
birth_Rate = input_data["population_demographic"]["birth_rate"]

print(country_code)

exp_path = validation_path
output_path = Path(exp_path) / "output"
analysis_path = Path(exp_path) / "analysis"
os.makedirs(analysis_path, exist_ok=True)

print(data_path)
print(output_path)
print(analysis_path)

# %% [markdown]
#  ## Pixel level

# %%
path_obj = Path(output_path)
if not path_obj.exists() or not path_obj.is_dir():
    raise NotADirectoryError(f"Path {output_path} is not a valid directory.")
db_files = list(path_obj.glob("*.db"))
if len(db_files) == 0:
    raise FileNotFoundError(f"No .db files found in directory {output_path}.")

agg_population_pixel = pd.DataFrame(columns=["monthly_data_id", "location_id", "population"])
agg_treatment_pixel  = pd.DataFrame(columns=["monthly_data_id", "location_id", "treatments"])
agg_clinical_episodes_pixel  = pd.DataFrame(columns=["monthly_data_id", "location_id", "clinical_episodes"])
agg_prevalence_2_to_10_pixel  = pd.DataFrame(columns=["monthly_data_id", "location_id", "pfpr_2to10"])
agg_clinical_episodes_2_to_10_pixel  = pd.DataFrame(columns=["monthly_data_id", "location_id", "clinical_episodes_2_to_10"])
agg_prevalence_under_5_pixel  = pd.DataFrame(columns=["monthly_data_id", "location_id", "pfpr_under5"])
agg_clinical_episodes_under_5_pixel = pd.DataFrame(columns=["monthly_data_id", "location_id", "clinical_episodes_under5"])

''' Maybe process agg_non_treatment_pixel one day if we can make this code go any faster, already takes ~ 2min per replicate for NG-SE'''

clinical_episodes_sum_all_reps_pixel = []
clinical_episodes_2_to_10_sum_all_reps_pixel = []
clinical_episodes_under_5_sum_all_reps_pixel = []
rep = 0
for file in path_obj.glob("*.db"):
    rep += 1
    print(f"... Processing replicate {rep} / {len(db_files)}")
    data = get_table(file, "monthly_site_data_cell")
    print(f"Data frame shape for replicate {rep} from file {file.name}: {data.shape}")

    if data.empty:
        raise Exception(f"Data frame is empty for replicate {rep} from file {file.name}")

    clinical_episodes_2_to_10_pixel = data[
        [
            "monthly_data_id",
            "location_id",
            "clinical_episodes_by_age_class_2_3",
            "clinical_episodes_by_age_class_3_4",
            "clinical_episodes_by_age_class_4_5",
            "clinical_episodes_by_age_class_5_6",
            "clinical_episodes_by_age_class_6_7",
            "clinical_episodes_by_age_class_7_8",
            "clinical_episodes_by_age_class_8_9",
            "clinical_episodes_by_age_class_9_10",
        ]
    ].copy()
    print("Copied clinical_episodes_2_to_10_pixel data frame for replicate {rep} from file {file.name}")
    clinical_episodes_2_to_10_pixel["clinical_episodes_2_to_10"] = clinical_episodes_2_to_10_pixel[
        [
            "clinical_episodes_by_age_class_2_3",
            "clinical_episodes_by_age_class_3_4",
            "clinical_episodes_by_age_class_4_5",
            "clinical_episodes_by_age_class_5_6",
            "clinical_episodes_by_age_class_6_7",
            "clinical_episodes_by_age_class_7_8",
            "clinical_episodes_by_age_class_8_9",
            "clinical_episodes_by_age_class_9_10",
        ]
    ].sum(axis=1)
    print("Calculated clinical_episodes_2_to_10 for replicate {rep} from file {file.name}")

    clinical_episodes_under_5_pixel = data[
        [
            "monthly_data_id",
            "location_id",
            "clinical_episodes_by_age_class_0_1",
            "clinical_episodes_by_age_class_1_2",
            "clinical_episodes_by_age_class_2_3",
            "clinical_episodes_by_age_class_3_4",
            "clinical_episodes_by_age_class_4_5",
        ]
    ].copy()
    print("Copied clinical_episodes_under_5_pixel data frame for replicate {rep} from file {file.name}")
    clinical_episodes_under_5_pixel["clinical_episodes_under5"] = clinical_episodes_under_5_pixel[
        [
            "clinical_episodes_by_age_class_0_1",
            "clinical_episodes_by_age_class_1_2",
            "clinical_episodes_by_age_class_2_3",
            "clinical_episodes_by_age_class_3_4",
            "clinical_episodes_by_age_class_4_5",
        ]
    ].sum(axis=1)
    print("Calculated clinical_episodes_under5 for replicate {rep} from file {file.name}")
    
    clinical_episodes_sum_all_reps_pixel.append(data["clinical_episodes"].sum())
    clinical_episodes_2_to_10_sum_all_reps_pixel.append(clinical_episodes_2_to_10_pixel["clinical_episodes_2_to_10"].sum())
    clinical_episodes_under_5_sum_all_reps_pixel.append(clinical_episodes_under_5_pixel["clinical_episodes_under5"].sum())
    
    # Add a column to the agg_* data frames from data
    try:
        agg_population_pixel = agg_population_pixel.merge(
            data[["monthly_data_id", "location_id", "population"]].copy(),
            how="outer",
            on=["monthly_data_id", "location_id"],
            suffixes=("", f"_{rep}"),
        )
        agg_treatment_pixel = agg_treatment_pixel.merge(
            data[["monthly_data_id", "location_id", "treatments"]].copy(),
            how="outer",
            on=["monthly_data_id", "location_id"],
            suffixes=("", f"_{rep}"),
        )
        agg_clinical_episodes_pixel = agg_clinical_episodes_pixel.merge(
            data[["monthly_data_id", "location_id", "clinical_episodes"]].copy(),
            how="outer",
            on=["monthly_data_id", "location_id"],
            suffixes=("", f"_{rep}"),
        )
        agg_prevalence_2_to_10_pixel = agg_prevalence_2_to_10_pixel.merge(
            data[["monthly_data_id", "location_id", "pfpr_2to10"]].copy(),
            how="outer",
            on=["monthly_data_id", "location_id"],
            suffixes=("", f"_{rep}"),
        )
        
        agg_clinical_episodes_2_to_10_pixel = agg_clinical_episodes_2_to_10_pixel.merge(
            clinical_episodes_2_to_10_pixel[["monthly_data_id", "location_id", "clinical_episodes_2_to_10"]].copy(),
            how="outer",
            on=["monthly_data_id", "location_id"],
            suffixes=("", f"_{rep}"),
        )
        agg_prevalence_under_5_pixel = agg_prevalence_under_5_pixel.merge(
            data[["monthly_data_id", "location_id", "pfpr_under5"]].copy(),
            how="outer",
            on=["monthly_data_id", "location_id"],
            suffixes=("", f"_{rep}"),
        )
        agg_clinical_episodes_under_5_pixel = agg_clinical_episodes_under_5_pixel.merge(
            clinical_episodes_under_5_pixel[["monthly_data_id", "location_id", "clinical_episodes_under5"]].copy(),
            how="outer",
            on=["monthly_data_id", "location_id"],
            suffixes=("", f"_{rep}"),
        )
    except Exception as e:
        error(f"Error processing replicate {rep}: {e}")
    
    info(f"Processed replicate {rep} from file {file.name}")
    # print columns of agg clincal episodes  pixel
    print(f"Columns of agg_clinical_episodes_pixel: {agg_clinical_episodes_pixel.columns.tolist()}")
    
print(f"All replicates processed. Total replicates: {rep}")

# %%
agg_clinical_episodes_pixel.head()

# %%
agg_population_pixel = agg_population_pixel.drop(columns=["population"])
agg_treatment_pixel = agg_treatment_pixel.drop(columns=["treatments"])
agg_clinical_episodes_pixel = agg_clinical_episodes_pixel.drop(columns=["clinical_episodes"])
agg_prevalence_2_to_10_pixel = agg_prevalence_2_to_10_pixel.drop(columns=["pfpr_2to10"])
agg_clinical_episodes_2_to_10_pixel = agg_clinical_episodes_2_to_10_pixel.drop(columns=["clinical_episodes_2_to_10"])
agg_prevalence_under_5_pixel = agg_prevalence_under_5_pixel.drop(columns=["pfpr_under5"])
agg_clinical_episodes_under_5_pixel = agg_clinical_episodes_under_5_pixel.drop(columns=["clinical_episodes_under5"])

print(agg_population_pixel.head())
print(agg_treatment_pixel.head())
print(agg_clinical_episodes_pixel.head())
print(agg_prevalence_2_to_10_pixel.head())
print(agg_clinical_episodes_2_to_10_pixel.head())
print(agg_prevalence_under_5_pixel.head())
print(agg_clinical_episodes_under_5_pixel.head())

# %%
print(f"Saving aggregated data to {analysis_path}")

agg_prevalence_2_to_10_pixel.to_csv(f"{analysis_path}/agg_prevalence_2_to_10_pixel.csv", index=False)
agg_clinical_episodes_2_to_10_pixel.to_csv(f"{analysis_path}/agg_clinical_episodes_2_to_10_pixel.csv", index=False)
agg_prevalence_under_5_pixel.to_csv(f"{analysis_path}/agg_prevalence_under_5_pixel.csv", index=False)
agg_clinical_episodes_under_5_pixel.to_csv(f"{analysis_path}/agg_clinical_episodes_under_5_pixel.csv", index=False)
agg_population_pixel.to_csv(f"{analysis_path}/agg_population_pixel.csv", index=False)
agg_treatment_pixel.to_csv(f"{analysis_path}/agg_treatment_pixel.csv", index=False)
agg_clinical_episodes_pixel.to_csv(f"{analysis_path}/agg_clinical_episodes_pixel.csv", index=False)

print(f"Saved aggregated data to {analysis_path}")

# %%
mean_clinical_episodes_sum_all_reps_pixel = pd.Series(clinical_episodes_sum_all_reps_pixel).mean()
mean_clinical_episodes_2_to_10_sum_all_reps_pixel = pd.Series(clinical_episodes_2_to_10_sum_all_reps_pixel).mean()
mean_clinical_episodes_under_5_sum_all_reps_pixel = pd.Series(clinical_episodes_under_5_sum_all_reps_pixel).mean()


print(f"Average total clinical episodes across replicates: {mean_clinical_episodes_sum_all_reps_pixel:,.0f}")
print(f"Average total clinical episodes (2-10) across replicates: {mean_clinical_episodes_2_to_10_sum_all_reps_pixel:,.0f}")
print(f"Average total clinical episodes (under 5) across replicates: {mean_clinical_episodes_under_5_sum_all_reps_pixel:,.0f}")

# %%
months = np.sort(agg_clinical_episodes_pixel["monthly_data_id"].unique())
end_month = int(months[-1]) + 1
start_month = end_month - 12

mean_treatment_pixel = (
    agg_treatment_pixel.loc[agg_treatment_pixel["monthly_data_id"].between(start_month, end_month, inclusive="left")]
    .copy()
    .groupby("location_id")
    .sum()
)
mean_treatment_pixel = mean_treatment_pixel.drop(columns=["monthly_data_id"])
# mean_treatment = mean_treatment.drop(columns=["clinical_episodes"])
mean_treatment_pixel["mean"] = mean_treatment_pixel.mean(axis=1)

mean_clinical_episodes_pixel = (
    agg_clinical_episodes_2_to_10_pixel.loc[agg_clinical_episodes_2_to_10_pixel["monthly_data_id"].between(start_month, end_month, inclusive="left")]
    .copy()
    .groupby("location_id")
    .sum()
)
mean_clinical_episodes_pixel = mean_clinical_episodes_pixel.drop(columns=["monthly_data_id"])
mean_clinical_episodes_pixel["mean"] = mean_clinical_episodes_pixel.mean(axis=1)
mean_clinical_episodes_pixel["std"] = mean_clinical_episodes_pixel.std(axis=1)

mean_population_pixel = (
    agg_population_pixel.loc[agg_population_pixel["monthly_data_id"].between(start_month, end_month, inclusive="left")]
    .copy()
    .groupby("location_id")
    .mean()
)
mean_population_pixel = mean_population_pixel.drop(columns=["monthly_data_id"])
# mean_population = mean_population.drop(columns=["population"])
mean_population_pixel["mean"] = mean_population_pixel.mean(axis=1)
mean_population_pixel["std"] = mean_population_pixel.std(axis=1)

mean_prevalence_2_to_10_pixel = (
    agg_prevalence_2_to_10_pixel.loc[
        agg_prevalence_2_to_10_pixel["monthly_data_id"].between(start_month, end_month, inclusive="left")
    ]
    .copy()
    .groupby("location_id")
    .mean()
)
mean_prevalence_2_to_10_pixel = mean_prevalence_2_to_10_pixel.drop(columns=["monthly_data_id"])
# mean_prevalence_2_to_10 = mean_prevalence_2_to_10.drop(columns=["pfpr_2to10"])
mean_prevalence_2_to_10_pixel["mean"] = mean_prevalence_2_to_10_pixel.mean(axis=1)
mean_prevalence_2_to_10_pixel["std"] = mean_prevalence_2_to_10_pixel.std(axis=1)

mean_prevalence_under_5_pixel = (
    agg_prevalence_under_5_pixel.loc[
        agg_prevalence_under_5_pixel["monthly_data_id"].between(start_month, end_month, inclusive="left")
    ]
    .copy()
    .groupby("location_id")
    .mean()
)
mean_prevalence_under_5_pixel = mean_prevalence_under_5_pixel.drop(columns=["monthly_data_id"])
# mean_prevalence_under_5 = mean_prevalence_under_5.drop(columns=["pfpr_under5"])
mean_prevalence_under_5_pixel["mean"] = mean_prevalence_under_5_pixel.mean(axis=1)
mean_prevalence_under_5_pixel["std"] = mean_prevalence_under_5_pixel.std(axis=1)

mean_clinical_episodes_pixel.to_csv(f"{analysis_path}/mean_clinical_episodes_pixel.csv")
mean_treatment_pixel.to_csv(f"{analysis_path}/mean_treatment_pixel.csv")
mean_prevalence_2_to_10_pixel.to_csv(f"{analysis_path}/mean_prevalence_2_to_10_pixel.csv")
mean_prevalence_under_5_pixel.to_csv(f"{analysis_path}/mean_prevalence_under_5_pixel.csv")
mean_population_pixel.to_csv(f"{analysis_path}/mean_population_pixel.csv")

print(f"Saved mean data to {analysis_path}")



