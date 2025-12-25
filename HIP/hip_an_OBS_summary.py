# source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pycorr

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
argparser.add_argument('--chain_root', type=str, default=None, help='Root path of the HOD chain files')
args = argparser.parse_args()

tracer = args.tracer
zmin = args.zmin
zmax = args.zmax
chain_root = args.chain_root
if args.work_dir is not None:
    WORK_DIR = Path(args.work_dir)
else:
    WORK_DIR = THIS_REPO / "HIP/test" / f"{tracer}_{zmin}_{zmax}"
print(f"Working directory: {WORK_DIR}\n")

# ========== define the sample ==========

# hip = HIPanOBSample(tracer=tracer, zmin=zmin, zmax=zmax, work_dir=WORK_DIR)
hip = HIPanOBSample(cfg_file=WORK_DIR / "config.yaml")

# ========== plot sampled clusterings ==========

hip.sample_HOD_measure_ps()
# dirEZmocks = '/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z1_c302_fnl1200/'
dirEZmocks = '/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z1_c302/'
hip.sample_HOD_plot_ps(dirEZmocks=dirEZmocks)

# ========== summary results ==========

results = hip.combine_chains()
print("Combined HOD fitting results:")
print(results)

# ========== save configurations ==========

hip.save_cfg()
print("Done. Configuration saved.\n")
