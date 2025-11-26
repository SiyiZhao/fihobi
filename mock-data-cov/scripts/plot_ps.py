# !/usr/bin/env python3
# the workdir is ~/projects/fihobi/mock-data-cov/
# pypower requires `source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main` on NERSC

import argparse
import numpy as np
import glob
from pypower import PowerSpectrumMultipoles
from matplotlib import pyplot as plt
import matplotlib as mpl
import os
mpl.rc_file('../fig/matplotlibrc')
color = ['#1f77b4', '#ff7f0e', '#9467bd', '#d62728', '#2ca02c', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

def parse_args():
    parser = argparse.ArgumentParser(description='Plot power spectra for a redshift bin.')
    parser.add_argument('--tag', type=str, required=True, help='Tag for the mock (e.g., z1, z2, etc.)')
    parser.add_argument('--dirEZmocks', type=str, help='Directory of EZmocks to plot. If empty, skip EZmocks plotting.')
    parser.add_argument('--base', type=str, help='Base directory for the mocks')
    return parser.parse_args()
args = parse_args()
tag = args.tag
dirEZmocks = args.dirEZmocks if args.dirEZmocks else None
base = args.base if args.base else 'c302_dv'
if dirEZmocks is not None:
    if not os.path.exists(dirEZmocks):
        print(f"Warning: dirEZmocks '{dirEZmocks}' not found; skipping EZmocks plotting")
        dirEZmocks = None

# Data -------------------------------------------------------------------------
z_mock = {'z1': 0.95, 'z2': 1.25, 'z3': 1.55, 'z4': 2.0, 'z5': 2.5, 'z6': 3.0}
z = z_mock[tag]

pdir='/pscratch/sd/s/siyizhao/desi-dr2-hod/'
data = {
    'c300_dv': {'dir': pdir+f'mocks/Abacus_pngbase_c300_ph000/z{z:.3f}/galaxies_rsd_dv/', 
                'label': 'fNL=30, dv', 'color': color[2], 'lstyle': ':'},
    'c302': {'dir': pdir+f'mocks/Abacus_pngbase_c302_ph000/z{z:.3f}/galaxies_rsd/', 
             'label': 'fNL=100', 'color': color[1], 'lstyle': '--'},
    'c302_dv': {'dir': pdir+f'mocks/Abacus_pngbase_c302_ph000/z{z:.3f}/galaxies_rsd_dv/', 
                'label': 'fNL=100, dv', 'color': color[0], 'lstyle': '--'},
    'c302_A_dv': {'dir': pdir+f'mocks_base-A-dv/Abacus_pngbase_c302_ph000/z{z:.3f}/galaxies_rsd_dv/', 
                  'label': 'fNL=100, dv, A', 'color': color[3], 'lstyle': '-.'},
    'c302_B_dv': {'dir': pdir+f'mocks_base-B-dv/Abacus_pngbase_c302_ph000/z{z:.3f}/galaxies_rsd_dv/', 
                  'label': 'fNL=100, dv, B', 'color': color[4], 'lstyle': '-.'},
    'c302_v2': {'dir': pdir+f'mocks_base_v2/Abacus_pngbase_c302_ph000/z{z:.3f}/galaxies_rsd/', 
                'label': 'fNL=100, v2', 'color': color[1], 'lstyle': '-'},
    'c302_dv_v2': {'dir': pdir+f'mocks_base-dv_v2/Abacus_pngbase_c302_ph000/z{z:.3f}/galaxies_rsd_dv/',
                   'label': 'fNL=100, dv, v2', 'color': color[0], 'lstyle': '-'}
}

### power spectra loading 
for key in data.keys():
    i = list(data.keys()).index(key)
    d = data[key]['dir']
    if not os.path.exists(d):
        raise ValueError(f"Directory '{d}' not found!")
    poles = PowerSpectrumMultipoles.load(d + 'pypower_poles.npy')  # test loading
    k, p0 = poles(ell=0, return_k=True, complex=False)
    if i==0:
        k_1st = k
    else:
        if not np.allclose(k, k_1st, equal_nan=True):
            raise ValueError("k arrays do not match!")
    data[key]['p0'] = p0
# data['k'] = k

### define base
if base in data.keys():
    P0_base = data[base]['p0']
else:
    raise ValueError(f"Unknown base: {base}")

### EZmocks loading
if dirEZmocks is not None:
    files = glob.glob(dirEZmocks+f'/pypowerpoles_r*.npy')
    p0_ez = []
    for fn in files:
        poles = PowerSpectrumMultipoles.load(fn) 
        k_ez, p0 = poles(ell=0, return_k=True, complex=False)
        p0_ez.append(p0)
    p0_ez_avg = np.mean(p0_ez, axis=0)
    p0_err = np.std(p0_ez, axis=0)
    print(f"Loaded {len(files)} EZmock power spectra from {dirEZmocks}")

    
# Plot -------------------------------------------------------------------------

fig, axs = plt.subplots(2,1,constrained_layout=True,sharex='col',figsize=(8,8),gridspec_kw={'height_ratios': [3, 1]})

if dirEZmocks is not None:
    # top panel: EZmocks
    p = p0_ez[0]
    axs[0].plot(k_ez[1:], p[1:], color='gray', alpha=0.3, label='EZmock')
    for p in p0_ez[1:]:
        axs[0].plot(k_ez[1:], p[1:], color='gray', alpha=0.3)
    axs[0].plot(k_ez[1:], p0_ez_avg[1:], color='black', lw=2, label='EZmock average')
    frac_ez = p0_ez_avg / P0_base - 1
    frac_err = p0_err / P0_base 
    axs[1].plot(k[1:], frac_ez[1:], color='black', lw=2)
    axs[1].fill_between(k[1:], - frac_err[1:], frac_err[1:], color='gray', alpha=0.5, label=r'EZmock $1\sigma$')    
# top panel: original spectra
for key in data.keys():
    p0 = data[key]['p0']
    axs[0].plot(k[1:], p0[1:], label=data[key]['label'], color=data[key]['color'], linestyle=data[key]['lstyle'])
axs[0].set_xscale('log')
axs[0].set_yscale('log')
axs[0].set_ylabel(r'$P_0(k)$ [$(\mathrm{Mpc}/h)^{3}$]')
axs[0].legend()

# bottom panel: fractional errors (P_variant - P_base) / P_base
for key in data.keys():
    p0 = data[key]['p0']
    frac = p0 / P0_base - 1
    axs[1].plot(k[1:], frac[1:], color=data[key]['color'], linestyle=data[key]['lstyle'])
axs[1].set_xscale('log')
axs[1].set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
axs[1].set_ylabel(r'$P^{\rm xx}/P^{\rm base}-1$')
# axs[1].axhspan(-0.05, 0.05, color='gray', alpha=0.5, label="5% error")
# axs[1].axhspan(-0.1, 0.1, color='gray', alpha=0.3)
ylim=0.2
axs[1].set_ylim(-ylim, ylim)
axs[1].legend()
plt.tight_layout()
fn=f'out/mock_ps{tag}_{base}.png'
plt.savefig(fn, dpi=300)
print(f'Saved figure to {fn}')
