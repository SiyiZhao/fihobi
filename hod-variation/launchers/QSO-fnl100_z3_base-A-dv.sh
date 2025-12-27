#!/bin/bash

#SBATCH --job-name=QSO-fnl100_z3_base-A-dv
#SBATCH --output=/global/homes/s/siyizhao/projects/fihobi/hod-variation/logs/%x_%j.log
#SBATCH --error=/global/homes/s/siyizhao/projects/fihobi/hod-variation/logs/%x_%j.err
#SBATCH --qos=regular
#SBATCH --account=desi
#SBATCH --time=8:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=64
#SBATCH -C cpu

source /global/common/software/desi/desi_environment.sh

export PYTHONPATH=$PYTHONPATH:$HOME/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/MultiNest/lib
export OMP_NUM_THREADS=64
outdir=/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv2/QSO-fnl100/z3_base-A-dv/
mkdir -p $outdir
config=configs/QSO-fnl100/z3_base-A-dv.yaml
cd /global/homes/s/siyizhao/projects/fihobi/hod-variation

# srun -n 1 -c 64 --cpu-bind=cores python -m abacusnbody.hod.prepare_sim_profiles --path2config $config
srun -N 2 -n 4 -c 64 --cpu-bind=cores python scripts/run_pmn.py --config $config > $outdir/run_v2.log 2>&1
srun -n 1 -c 64 --cpu-bind=cores python scripts/post.py --config $config > $outdir/post_v2.log 2>&1
