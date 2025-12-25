from pathlib import Path

def script_HIP(num: int, WORK_DIR: Path) -> str:
    script = f"""#!/bin/bash

export THIS_REPO=$HOME/projects/fihobi/
cd ${{THIS_REPO}}
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for cosmoprimo

WORK_DIR={WORK_DIR}
for i in {{0..{num-1}}}; do
    odir=${{WORK_DIR}}/HIP/mocks/r$i
    mkdir -p ${{odir}}
    srun -N 1 -n 1 -c 1 --cpu-bind=cores python HIP/fit_p_thecov.py $WORK_DIR $i > ${{odir}}/std.txt 2>&1 &
done 
wait
""".lstrip()
    return script