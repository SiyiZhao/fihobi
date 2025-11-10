#!/bin/bash
# Run EZmocks with PNG initial conditions on NERSC (Perlmutter) with adaptive parallelism
# Usage: run `bash genEZmocks.sh; exit` on an interactive allocation (salloc -A desi -C cpu -q interactive -t 04:00:00 -N <num_nodes> --exclusive)

# load cosmodesi for pypower
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main 

cd /global/homes/s/siyizhao/projects/fihobi/mock-data-cov

# === Set and Create output dirs ===
odir=/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z1_c302
config=configs/ezQSOz1fnl100.yaml
# we recommend to soft link logs and confs to scratch for faster I/O and enough space
mkdir -p logs/ezmock/ conf_2lpt/params_2lpt/ /pscratch/sd/s/siyizhao/2LPTdisp/ "$odir"

TOTAL=400      # total number of EZmocks to generate
START=12101    # starting ID
CPUS=32        # each mock uses 32 CPUs

# === Detect environment ===
# Get number of nodes and total CPUs
NNODES=${SLURM_NNODES:-1}
NTASKS_PER_NODE=$((128 / CPUS))   # 128 CPUs per Perlmutter node
NPROC=$((NNODES * NTASKS_PER_NODE))

echo "=== EZmock parallel launcher ==="
echo "Nodes: $NNODES, Tasks per node: $NTASKS_PER_NODE, Total concurrent tasks: $NPROC"
echo "Each task uses $CPUS CPUs"

# === Launch tasks ===
for ((k=0; k<TOTAL; k++)); do
    id=$((START + k))
    # each srun gets 1 task, exclusive CPUs so tasks don't overlap
    srun -N1 -n1 --cpus-per-task=$CPUS --exclusive --cpu-bind=cores \
        --output=logs/ezmock/id${id}.log \
        env OMP_NUM_THREADS=$CPUS MKL_NUM_THREADS=$CPUS \
        python scripts/genEZmockPNG.py "$id" "$odir" "$config" &
    
    # control number of concurrent tasks
    if [ $(( (k + 1) % NPROC )) -eq 0 ]; then
        wait
        echo "--- Finished batch $((k / NPROC + 1)) ---"
    fi
done

wait
echo "All EZmock tasks completed."

# === Optional cleanup ===
rm -f rand_ampl.bin rand_phase.bin
# rm conf_2lpt/params_2lpt/r*.param
