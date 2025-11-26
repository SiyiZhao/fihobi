#!/bin/bash

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
cd /global/homes/s/siyizhao/projects/fihobi/inference

name=bphi_QSO-z6_fNL100_base-A-dv
odir=/pscratch/sd/s/siyizhao/desilike/fit_PNG_bias/${name}
mkdir -p ${odir}

srun -n 1 -c 64 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python scripts/fit_PNG_bias.py ${name} ${odir} > ${odir}/std.log 2>&1
