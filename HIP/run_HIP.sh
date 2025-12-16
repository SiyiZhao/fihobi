#!/bin/bash

cd /global/homes/s/siyizhao/projects/fihobi/HIP

# ###=== Prepare HIP configuration
# python3 prep_config.py --Assembly True --version v2.1
# # python3 prep_config.py --version v2_logpr


# ###=== HOD fitting
# cd ../hod-variation/
# echo "[move] -> ../hod-variation/"
# python3 prep_configs.py --config ../HIP/HIP.yaml 
# ## this prepare configs for all tracers at all redshifts
# ###!!! submit HOD fitting jobs, eg: `sbatch launchers/QSO-fnl100_z6_base.sh`
# ###!!! analysis fitting results

# ###=== sample HOD paramters
# source /global/common/software/desi/desi_environment.sh
# export PYTHONPATH=$PYTHONPATH:$HOME/lib

# srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi -n 1 -c 64 python scripts/sampleHOD.py --cfgs4HIP ../HIP/HIP.yaml 
# python scripts/sampleHOD_plot.py --cfgs4HIP ../HIP/HIP.yaml 

# ###=== measure mock power spectrum, bias, nbar -> thecov covariance matrix
# cd ../HIP/
# echo "[move] -> ../HIP/"
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for cosmoprimo
# python data_thecov.py 

# ###=== fit p with mock power spectrum + thecov covariance matrix
# # python fit_p_thecov.py

name=QSO-z6_fNL100_base_1
# odir=out/test_kbin/${name}
# odir=out/fit_PNG_bias_v2/${name}
odir=works/${name}
mkdir -p ${odir}
srun -n 1 -c 64 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python fit_p_thecov.py ${name} ${odir}  "r1"> ${odir}/std.txt 2>&1