#!/bin/bash

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib
outdir=/pscratch/sd/s/siyizhao/fihobi/mocks_bestfit_y3xi0
# outdir=/pscratch/sd/s/siyizhao/fihobi/mocks_map_y3xi0
mkdir -p $outdir
cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

### only prepare once for each snapshot
# srun --cpu_bind=cores python -m abacusnbody.hod.prepare_sim --path2config config/abacus_hod.yaml 

srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python mock.py --path2config config/bestfit_y3xi0.yaml > $outdir/stdout.log 2> $outdir/stderr.log
# srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python mock.py --path2config config/map_y3xi0.yaml > $outdir/stdout.log 2> $outdir/stderr.log

exit

# then run compare_xipoles.py to compare the xi0 (and xi2 although it is not used for fitting) from the mock and the data