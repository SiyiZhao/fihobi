#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

export PYTHONPATH=$PYTHONPATH:$HOME/lib/LSS/py

weight_type=pip_angular_bitwise
tracer=QSO
cd /global/u1/s/siyizhao/projects/fihobi
outdir=/global/cfs/cdirs/desicollab/users/siyizhao/Y3/loa-v1/v2/PIP
mkdir -p ${outdir}

zlim="0.8 3.5"
sample_name=QSO_z0p800_3p500
# run for rppi
corr=rppi
srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g clustering/xirunpc.py --tracer ${tracer} --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim $zlim --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/logs/${corr}_${sample_name}.log 2>&1 
# run for smu
corr=smu
srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g clustering/xirunpc.py --tracer ${tracer} --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim $zlim --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/logs/${corr}_${sample_name}.log 2>&1 
