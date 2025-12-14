from pathlib import Path

def script_HOD(
    config_path: str,
    chain_path: str,
    workdir: Path,
    *,
    version: str = "v2",
    job_name: str | None = None,
    logs_dir: str | None = None,   # defaults to workdir/logs if None
    account: str = "desi",
    qos: str = "regular",
    constraint: str = "cpu",
    time_hms: str = "08:00:00",
    ntasks: int = 4,
    cpus_per_task: int = 64,
    omp_num_threads: int = 64,
) -> str:
    if job_name is None:
        job_name = Path(config_path).stem
    if logs_dir is None:
        logs_dir = str(Path(workdir) / "logs")
    ntasks_per_node = 128 // cpus_per_task
    nodes = ntasks // ntasks_per_node + (1 if ntasks % ntasks_per_node > 0 else 0)
    
    script = f"""#!/bin/bash

#SBATCH --job-name={job_name}
#SBATCH --output={logs_dir}/%x_%j.log
#SBATCH --error={logs_dir}/%x_%j.err
#SBATCH --qos={qos}
#SBATCH --account={account}
#SBATCH --time={time_hms}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={ntasks_per_node}
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH -C {constraint}

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$HOME/lib:$PYTHONPATH
export LD_LIBRARY_PATH=$HOME/lib/MultiNest/lib:$LD_LIBRARY_PATH
export OMP_NUM_THREADS={omp_num_threads}

export THIS_REPO=$HOME/projects/fihobi/
cd ${{THIS_REPO}}
outdir={chain_path}
mkdir -p $outdir
config={config_path}

# srun -n 1 -c 64 --cpu-bind=cores python -m abacusnbody.hod.prepare_sim_profiles --path2config $config
srun -N {nodes} -n {ntasks} -c {cpus_per_task} --cpu-bind=cores python hod-variation/scripts/run_pmn.py --config $config > $outdir/run_{version}.log 2>&1
srun -n 1 -c 64 --cpu-bind=cores python hod-variation/scripts/post.py --config $config > $outdir/post_{version}.log 2>&1
""".lstrip()
    return script
