import os, sys
# Add the source directory to the PYTHONPATH.
sys.path.insert(0, '../src')
from abacus_helper import path_to_catalog, read_catalog
from pypower_helpers import run_pypower_redshift

config = sys.argv[1]  # e.g. configs/QSO-fnl100/z6_base.yaml

num = 10
for i in range(num):
    sample_id = f'base_{i}'
    print(f'[info] sample_id = {sample_id}')
    path = path_to_catalog(config=config, tracer='QSO', custom_prefix=sample_id)
    out_path = os.path.dirname(path) + f'/{sample_id}_pypower_poles.npy'
    pos = read_catalog(path)
    poles = run_pypower_redshift(pos[:,0], pos[:,1], pos[:,2])

    print('Shot noise is {:.4f}.'.format(poles.shotnoise)) # cross-correlation, shot noise is 0.
    print('Normalization is {:.4f}.'.format(poles.wnorm))

    ## save
    poles.save(out_path)
    print(f'[write] pypower poles -> {out_path}.')
