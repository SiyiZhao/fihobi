#!/bin/bash

#SBATCH --job-name=QSO-fnl100_z1_base-A-dv
#SBATCH --output=/global/homes/s/siyizhao/projects/fihobi/hod-variation/logs/%x_%j.log
#SBATCH --error=/global/homes/s/siyizhao/projects/fihobi/hod-variation/logs/%x_%j.err
#SBATCH --qos=regular
#SBATCH --account=desi
#SBATCH --time=6:00:00
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=64
#SBATCH -C cpu

source /global/common/software/desi/desi_environment.sh

export PYTHONPATH=$PYTHONPATH:$HOME/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/MultiNest/lib
export OMP_NUM_THREADS=64
outdir=/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl100/z1_base-A-dv/
mkdir -p $outdir
config=configs/QSO-fnl100/z1_base-A-dv.yaml
cd /global/homes/s/siyizhao/projects/fihobi/hod-variation

srun -n 4 -c 64 python -m abacusnbody.hod.prepare_sim_profiles --path2config $config
srun -n 4 -c 64 python scripts/run_pmn.py --config $config > $outdir/run.log 2>&1
srun -n 1 -c 64 python scripts/post.py --config $config > $outdir/post.log 2>&1
