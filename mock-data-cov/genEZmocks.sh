#!/bin/bash
# generate EZmocks with PNG initial conditions
# Usage: run `bash genEZmocks.sh ;exit` on an interactive allocation (salloc -A desi -C cpu -q interactive -t 04:00:00 -N 1)

cd /global/homes/s/siyizhao/projects/fihobi/mock-data-cov

mkdir -p logs/ configs/params_2lpt/ 
mkdir -p /pscratch/sd/s/siyizhao/2LPTdisp/
odir=/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z4_c300
mkdir -p "$odir"

TOTAL=10  # total number of EZmocks to generate
START=7001  # starting EZmock ID
NPROC=8
CPUS=16

for ((k=0;k<TOTAL;k++)); do
    id=$((START + k))
    # each srun gets 1 task, 16 cpus, exclusive so tasks don't overlap
    srun -N1 -n1 --cpus-per-task=$CPUS --exclusive --cpu-bind=cores \
        --output=logs/ezmock_%j_%t_id${id}.out \
        env OMP_NUM_THREADS=$CPUS MKL_NUM_THREADS=$CPUS \
        python scripts/genEZmockPNG.py "$id" &
    # 每启动 NPROC 个后台任务就等待它们完成，保证并发不超过 NPROC
    if (( (k+1) % NPROC == 0 )); then
        wait
    fi
done
wait
