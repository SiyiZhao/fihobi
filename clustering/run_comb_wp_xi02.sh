#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

export PYTHONPATH=$PYTHONPATH:$HOME/lib/LSS/py

weight_type=pip_angular_bitwise
version=v1.1/PIP
verspec=loa-v1
# corr=rppi
corr=smu
tracer=QSO
outdir=/global/cfs/cdirs/desi/users/siyizhao/Y3/$verspec/$version
mkdir -p $outdir

# srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g /global/homes/s/siyizhao/projects/fihobi/clustering/xirunpc.py --tracer QSO --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim 0.8 1.1 --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/${corr}_stdout.log 2> $outdir/${corr}_stderr.log

outdir=/global/homes/s/siyizhao/projects/fihobi/data/hodfit
mkdir -p $outdir
srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python combine_wp_xi02.py -i '/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v1.1/PIP/cosmo_0/' -t $tracer -o $outdir/${tracer}_data_cov_arocher_cosmo0.h5 > $outdir/combforfit_cosmo0_stdout.log 2> $outdir/combforfit_cosmo0_stderr.log

exit
