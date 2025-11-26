#!/bin/bash

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
cd /global/homes/s/siyizhao/projects/fihobi/inference

name=QSO-z4_fNL30_base-dv
odir=/pscratch/sd/s/siyizhao/desilike/fit_p/${name}
mkdir -p ${odir}

srun -n 1 -c 64 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python scripts/fit_PNG_bias.py ${name} ${odir} > ${odir}/std.log 2>&1
