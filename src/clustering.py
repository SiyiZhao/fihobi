from pathlib import Path
THIS_REPO = Path(__file__).parent.parent

def script_clustering(
    tracer: str, 
    zmin: float, 
    zmax: float,
    path2ObsClus: Path,
    *,
    sample_name: str="sample", 
    weight_type: str="pip_angular_bitwise"
    ) -> str:
    script = f"""#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

export PYTHONPATH=$PYTHONPATH:$HOME/lib/LSS/py

weight_type={weight_type}
tracer={tracer}
cd {THIS_REPO}
outdir={path2ObsClus}
mkdir -p ${{outdir}}

zlim="{zmin} {zmax}"
sample_name={sample_name}
# run for rppi
corr=rppi
srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g clustering/xirunpc.py --tracer ${{tracer}} --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim $zlim --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/logs/${{corr}}_${{sample_name}}.log 2>&1 
# run for smu
corr=smu
srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g clustering/xirunpc.py --tracer ${{tracer}} --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim $zlim --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/logs/${{corr}}_${{sample_name}}.log 2>&1 
""".lstrip()
    return script
