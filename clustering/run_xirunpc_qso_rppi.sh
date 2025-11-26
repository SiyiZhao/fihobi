#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

export PYTHONPATH=$PYTHONPATH:$HOME/lib/LSS/py

weight_type=pip_angular_bitwise
version=v2/PIP
verspec=loa-v1
corr=rppi
tracer=QSO
outdir=/global/cfs/cdirs/desi/users/siyizhao/Y3/$verspec/$version
mkdir -p $outdir

# define z ranges
# zlims=("1.7 2.3" "2.3 2.8" "2.8 3.5")
# zlim_names=("z1p7_2p3" "z2p3_2p8" "z2p8_3p5")
zlims=("2.8 3.5")
zlim_names=("z2p8_3p5")

# submit jobs for different z ranges sequentially
for i in "${!zlims[@]}"; do
    zlim="${zlims[$i]}"
    zlim_name="${zlim_names[$i]}"
    
    srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g /global/homes/s/siyizhao/projects/fihobi/clustering/xirunpc.py --tracer ${tracer} --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim $zlim --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/${corr}_${tracer}_${zlim_name}_stdout.log 2> $outdir/${corr}_${tracer}_${zlim_name}_stderr.log
    
done
