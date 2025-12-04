#!/bin/bash

cd /global/homes/s/siyizhao/projects/fihobi/HIP

### Prepare HIP configuration
python3 prep_config.py

### HOD fitting
cd ../hod-variation/
python3 prep_configs.py --config ../HIP/HIP.yaml
###!!! submit HOD fitting jobs, eg: `sbatch launchers/QSO-fnl100_z6_base.sh`
###!!! analysis fitting results

### sample HOD paramters