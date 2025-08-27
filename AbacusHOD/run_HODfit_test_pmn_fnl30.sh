#!/bin/bash
#SBATCH -A desi
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 24:00:00
#SBATCH -N 1

source /global/common/software/desi/desi_environment.sh

export PYTHONPATH=$PYTHONPATH:$HOME/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/MultiNest/lib
# outdir=/pscratch/sd/s/siyizhao/fihobi/HOD_fit_test
outdir=/pscratch/sd/s/siyizhao/fihobi/HODfit_test_z0_fnl30
mkdir -p $outdir/pmn/

cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

srun -n 1 -c 64 --cpu_bind=cores python -m abacusnbody.hod.prepare_sim --path2config config/lrg_z0_test_fnl30.yaml

srun -n 4 -c 64 --cpu_bind=cores python fit_pmn.py --path2config config/lrg_z0_test_fnl30.yaml > $outdir/stdout.log 2> $outdir/stderr.log

