# source env/env.sh

import sys, os
src_path = os.path.abspath(os.path.join(os.environ.get("THIS_REPO"), 'src'))
sys.path.insert(0, src_path)
print(f"Added {src_path} to sys.path")
from HIPanOBSample import HIPanOBSample

tracer = 'QSO'
zmin = 2.8
zmax = 3.5

# define the sample
hip = HIPanOBSample(tracer=tracer, zmin=zmin, zmax=zmax)

# measure clustering
hip.measure_clustering(path_script=f"scripts/clustering_{tracer}_{zmin}_{zmax}.sh")

# HOD fitting
hip.prepare_HOD_fitting()