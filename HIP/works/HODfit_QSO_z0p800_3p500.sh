#!/bin/bash

#SBATCH --job-name=HODfit_QSO_z0p800_3p500
#SBATCH --output=/global/u1/s/siyizhao/projects/fihobi/HIP/test/QSO_0.8_3.5/logs/%x_%j.log
#SBATCH --error=/global/u1/s/siyizhao/projects/fihobi/HIP/test/QSO_0.8_3.5/logs/%x_%j.err
#SBATCH --qos=regular
#SBATCH --account=desi
#SBATCH --time=08:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=64
#SBATCH -C cpu

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$HOME/lib:$PYTHONPATH
export LD_LIBRARY_PATH=$HOME/lib/MultiNest/lib:$LD_LIBRARY_PATH
export OMP_NUM_THREADS=64
export MKL_NUM_THREADS=64

export THIS_REPO=$HOME/projects/fihobi/
cd ${THIS_REPO}
outdir=/pscratch/sd/s/siyizhao/fihobi/HIP_test/QSO_0.8_3.5/HOD_chains
mkdir -p $outdir
config=/global/u1/s/siyizhao/projects/fihobi/HIP/test/QSO_0.8_3.5/scripts/cfgHOD.yaml

# srun -n 1 -c 64 --cpu-bind=cores python -m abacusnbody.hod.prepare_sim_profiles --path2config $config
srun -N 2 -n 4 -c 64 --cpu-bind=cores python hod-variation/scripts/run_pmn.py --config $config > $outdir/run_v1.log 2>&1
srun -n 1 -c 64 --cpu-bind=cores python hod-variation/scripts/post.py --config $config > $outdir/post_v1.log 2>&1
