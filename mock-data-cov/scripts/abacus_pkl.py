import numpy as np
import os, sys
current_dir = os.getcwd()
source_dir = os.path.join(current_dir, "source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from pypower_helpers import run_pypower_redshift

data_fn = sys.argv[1]
out_path = sys.argv[2]
out_for_EZmock = sys.argv[3]

data = np.loadtxt(data_fn, skiprows=15)
x, y, z = data[:, 0], data[:, 1], data[:, 2]
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
np.savetxt(out_for_EZmock, array_form_powspec)
