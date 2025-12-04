import numpy as np
import os, sys
sys.path.insert(0, '../src')
from abacus_helper import path_to_mock_dir, read_AbacusHOD_cat
from pypower_helpers import run_pypower_redshift

config2Abacus = sys.argv[1]  # e.g. configs/QSO-fnl30/z4_base-dv.yaml
path2mock = path_to_mock_dir(config2Abacus)
data_fn = path2mock / 'QSOs.dat'
out_path = path2mock / 'pypower_poles.npy'
out_for_EZmock = path2mock / 'pypower2powspec.txt'


x, y, z = read_AbacusHOD_cat(data_fn)
poles = run_pypower_redshift(x,y,z)

print('Shot noise is {:.4f}.'.format(poles.shotnoise)) # cross-correlation, shot noise is 0.
print('Normalization is {:.4f}.'.format(poles.wnorm))

## save
poles.save(out_path)

## to powspec format
kbin = poles.edges[0]
kmin, kmax = kbin[:-1], kbin[1:]
kavg = poles.modes[0]
nmodes = poles.nmodes
k, pk0 = poles(ell=0, return_k=True, complex=False)
pk2 = poles(ell=2, return_k=False, complex=False)
array_form_powspec = np.vstack([k, kmin, kmax, kavg, nmodes, pk0, pk2]).T
np.savetxt(out_for_EZmock, array_form_powspec, header='kcen kmin kmax kavg nmod P_0 P_2')
