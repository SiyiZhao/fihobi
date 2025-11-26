#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

export PYTHONPATH=$PYTHONPATH:$HOME/lib/LSS/py

weight_type=pip_angular_bitwise
version=v2/PIP
verspec=loa-v1
tracer=QSO
outdir=/global/cfs/cdirs/desi/users/siyizhao/Y3/$verspec/$version
mkdir -p $outdir

# define z ranges
zlim="2.8 3.5"
zlim_name="z2p8_3p5"

# run for rppi
corr=rppi
srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g /global/homes/s/siyizhao/projects/fihobi/clustering/xirunpc.py --tracer ${tracer} --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim $zlim --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/${corr}_${tracer}_${zlim_name}_stdout.log 2> $outdir/${corr}_${tracer}_${zlim_name}_stderr.log

# run for smu
corr=smu
srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g /global/homes/s/siyizhao/projects/fihobi/clustering/xirunpc.py --tracer ${tracer} --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim $zlim --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/${corr}_${tracer}_${zlim_name}_stdout.log 2> $outdir/${corr}_${tracer}_${zlim_name}_stderr.log
