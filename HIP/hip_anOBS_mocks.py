# source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pypower and cosmoprimo

import sys, os, argparse
from pathlib import Path
THIS_REPO = Path(__file__).parent.parent
src_path = os.path.abspath(os.path.join(THIS_REPO, 'src'))
sys.path.insert(0, src_path)
print(f"Added {src_path} to sys.path\n")
from HIPanOBSample import HIPanOBSample

argparser = argparse.ArgumentParser(description="Analyze the HOD sampled mocks in the HIP framework.")
argparser.add_argument('--tracer', type=str, default='QSO', help='Tracer type, e.g., QSO')
argparser.add_argument('--zmin', type=float, default=2.8, help='Minimum redshift of the sample')
argparser.add_argument('--zmax', type=float, default=3.5, help='Maximum redshift of the sample')
argparser.add_argument('--work_dir', type=str, default=None, help='Working directory for the analysis')
args = argparser.parse_args()

tracer = args.tracer
zmin = args.zmin
zmax = args.zmax
if args.work_dir is not None:
    WORK_DIR = Path(args.work_dir)
else:
    WORK_DIR = THIS_REPO / "HIP/test" / f"{tracer}_{zmin}_{zmax}"
print(f"Working directory: {WORK_DIR}\n")

# ========== define the sample ==========

# hip = HIPanOBSample(tracer=tracer, zmin=zmin, zmax=zmax, work_dir=WORK_DIR)
hip = HIPanOBSample(cfg_file=WORK_DIR / "config.yaml")

# ========== fit p from the mocks ==========

priors = {
    'p': {'limits': (-1., 3.)},
    'sigmas': {'limits': (0., 20.)},
}
bestfit = hip.fit_p_from_mocks(priors=priors, nproc=20)

# ========== save configurations ==========

hip.save_cfg()
sys.stdout.flush() 
