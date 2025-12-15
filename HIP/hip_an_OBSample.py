# source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pycorr
# ln -s /pscratch/sd/s/siyizhao/fihobi/HIP_test test

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

hip = HIPanOBSample(tracer=tracer, zmin=zmin, zmax=zmax, work_dir=WORK_DIR)
# hip = HIPanOBSample(cfg_file=WORK_DIR / "config.yaml")

# ========== measure clustering ==========

hip.measure_clustering()

# ========== HOD fitting ==========

hip.prepare_HOD_fitting()

prior = {
    'logM_cut': (0, 11.0, 15.0, 'flat'),
    'logM1': (1, 10.0, 18.0, 'flat'),
    'sigma': (2, 0.0001, 3.0, 'flat'),
    'alpha': (3, -1, 3.0, 'flat'),
    'kappa': (4, 0.0, 10.0, 'flat'),
    'alpha_c': (5, 0, 3.0, 'flat'),
    'alpha_s': (6, -4, 2.0, 'log'),
    'Acent': (7, -10.0, 10.0, 'flat'),
    'Asat': (8, -15.0, 15.0, 'flat'),
}
hip.config_HOD_fitting(prior=prior, version='v1')

hip.fit_HOD(time_hms='08:00:00', ntasks=8)

# # ========== sample HOD parameters ==========

# chain_root = '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl100/z6_base-A/chain_v2.1_'
# samples = hip.sample_HOD_params(chain_root=chain_root, num=10, plot=True)
# hip.sample_HOD_mocks(params_list=samples, nthread=nthread, write_cat=True, want_2PCF=True, want_poles=True)

# ========== save configurations ==========

hip.save_cfg()
