#!/bin/bash

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
cd /global/homes/s/siyizhao/projects/fihobi/inference

for i in {4..9}; do
    name="QSO-z6_fNL100_base_${i}"
    odir="out/fit_PNG_bias_v2/${name}"
    mkdir -p "${odir}"
    srun -n 1 -c 64 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g \
        python scripts/fit_PNG_bias.py "${name}" "${odir}" > "${odir}/std.log" 2>&1 &
    if (( i % 2 == 0 )); then
        wait
    fi
done
wait
