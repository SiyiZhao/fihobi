# source /global/common/software/desi/desi_environment.sh 
# for the numba version compatibility for AbacusHOD

import sys, os
from pathlib import Path
THIS_REPO = Path(__file__).parent.parent
src_path = os.path.abspath(os.path.join(THIS_REPO, 'src'))
sys.path.insert(0, src_path)
print(f"Added {src_path} to sys.path\n")
from HIPanOBSample import HIPanOBSample

tracer = 'QSO'
# zmin = 0.8
zmin = 2.8
zmax = 3.5
WORK_DIR = THIS_REPO / "HIP/test" / f"{tracer}_{zmin}_{zmax}"
# WORK_DIR = THIS_REPO / "HIP/work" / f"{tracer}_{zmin}_{zmax}"
nthread = 64

# ========== define the sample ==========

# hip = HIPanOBSample(tracer=tracer, zmin=zmin, zmax=zmax, work_dir=WORK_DIR)
hip = HIPanOBSample(cfg_file=WORK_DIR / "config.yaml")

# ========== sample HOD parameters ==========

chain_root = '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl100/z6_base-A/chain_v2.1_'
samples = hip.sample_HOD_params(chain_root=chain_root, num=100, plot=True)
hip.sample_HOD_mocks(params_list=samples, nthread=nthread, write_cat=True, want_2PCF=True, want_poles=False)

# ========== save configurations ==========

hip.save_cfg()
