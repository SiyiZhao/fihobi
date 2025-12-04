#!/bin/bash

cd /global/homes/s/siyizhao/projects/fihobi/HIP

###=== Prepare HIP configuration
python3 prep_config.py #--Assembly True

###=== HOD fitting
cd ../hod-variation/
echo "[move] -> ../hod-variation/"
# python3 prep_configs.py --config ../HIP/HIP.yaml 
## this prepare configs for all tracers at all redshifts
###!!! submit HOD fitting jobs, eg: `sbatch launchers/QSO-fnl100_z6_base.sh`
###!!! analysis fitting results

###=== sample HOD paramters
source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib

srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi -n 1 -c 64 python scripts/sampleHOD.py --cfgs4HIP ../HIP/HIP.yaml 
python scripts/sampleHOD_plot.py --cfgs4HIP ../HIP/HIP.yaml 
