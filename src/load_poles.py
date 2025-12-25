import numpy as np
import glob, os
from pypower import PowerSpectrumMultipoles
from matplotlib import pyplot as plt
from io_def import path_to_poles


def load_poles_data(data):
    for i, key in enumerate(data.keys()):
        d = data[key]['path']
        if not os.path.exists(d):
            raise ValueError(f"Path '{d}' not found!")
        poles = PowerSpectrumMultipoles.load(d) 
        k, p0 = poles(ell=0, return_k=True, complex=False)
        if i==0:
            k_1st = k
        else:
            if not np.allclose(k, k_1st, equal_nan=True):
                raise ValueError("k arrays do not match!")
        data[key]['p0'] = p0
    return data, k_1st

def load_sampled_HOD_mocks(data, k_1st=None, num=1, sim_params=None, tracer=None, cmap='viridis'):
    cmap = plt.get_cmap(cmap)
    for i in range(num):
        key = f'r{i}'
        path2poles = path_to_poles(sim_params=sim_params, tracer=tracer, prefix=f'r{i}')
        poles = PowerSpectrumMultipoles.load(path2poles)
        k, p0 = poles(ell=0, return_k=True, complex=False)
        if not np.allclose(k, k_1st, equal_nan=True):
            raise ValueError("k arrays do not match!")
        data[key] = {
            'p0': p0,
            'color': cmap(i / num),
            'lstyle': ':',
            'label': None,
            # 'label': f'i{i}',
            'alpha': 0.3,
        }
    return data

def load_EZmocks(dirEZmocks, k_1st=None):
    files = glob.glob(dirEZmocks+f'/pypowerpoles_r*.npy')
    p0_ez = []
    for fn in files:
        poles = PowerSpectrumMultipoles.load(fn) 
        k_ez, p0 = poles(ell=0, return_k=True, complex=False)
        if not np.allclose(k_ez, k_1st, equal_nan=True):
            raise ValueError("k arrays do not match!")
        p0_ez.append(p0)
    p0_ez_avg = np.mean(p0_ez, axis=0)
    p0_err = np.std(p0_ez, axis=0)
    print(f"Loaded {len(files)} EZmock power spectra from {dirEZmocks}")
    return p0_ez, p0_ez_avg, p0_err
