#!/bin/bash

cd /work/tuv89272/Calibration_Pipeline_v7_NG-SE/_pre_calibration_population_growth_rate_validation || exit 1

nohup ./bin/MalaSim \
-i input/input_population_bins_beta_zero_pop_0.25.yml \
-r SQLiteMonthlyReporter \
-o output/pop_validation \
-j 0 \
-v 1 \
> 0.log 2>&1 &

echo $! > malaSim_0.pid
echo "MalaSim started in background"
echo "PID: $(cat malaSim_0.pid)"
echo "Log: 0.log"
