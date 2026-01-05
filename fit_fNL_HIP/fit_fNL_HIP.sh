#!/bin/bash

export THIS_REPO=$HOME/projects/fihobi/
cd ${THIS_REPO}

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

odir=fit_fNL_HIP/works/QSO_box_z3_base-A_c300_thecov
mkdir -p ${odir}
config=${odir}/config.yaml

python fit_fNL_HIP/prep_config.py ${config} ${odir}
srun -n 1 -c 64 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python fit_fNL_HIP/fit_fNL_with_HIP_box.py ${config} ${odir} > ${odir}/std.log 2>&1
