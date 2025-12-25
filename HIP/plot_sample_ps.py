# %%
# source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pypower
# python plot_sample_2PCF.py --WORKDIR test/QSO_2.8_3.5
import argparse
import numpy as np
from pypower import PowerSpectrumMultipoles
import glob
from matplotlib import pyplot as plt

# %%
from pathlib import Path
THIS_REPO = Path(__file__).parent.parent
import sys, os
src_path = os.path.abspath(os.path.join(THIS_REPO, 'src'))
sys.path.insert(0, src_path)
from HIPanOBSample import HIPanOBSample
from io_def import path_to_poles

# %%
def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--WORKDIR', type=str, required=True, help='Path to the working directory, should contain config.yaml.')
    args = parser.parse_args()
    return args

# %%
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

# %%
def load_sampled_HOD_mocks(data, k_1st=None, num=1):
    cmap = plt.get_cmap(hip.HIP['cmap'])
    for i in range(num):
        key = f'r{i}'
        path2poles = path_to_poles(sim_params=hip.cfgHOD['sim_params'], tracer=tracer, prefix=f'r{i}')
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

# %%
def load_EZmocks(dirEZmocks):
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
    
# %%
if __name__ == "__main__":
    args = argument_parser()
    WORK_DIR = args.WORKDIR
    hip = HIPanOBSample(cfg_file=WORK_DIR + "/config.yaml")
    tracer = hip.OBSample['tracer']
    zmin = hip.OBSample['zmin']
    zmax = hip.OBSample['zmax']
    path2cfgHOD = hip.cfg['HODfit']['path2cfgHOD']
    num = hip.HIP['num_samples']
    print(f"Number of samples to plot: {num}\n")

    dirEZmocks = '/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z6_c302_fnl300/'
    ### MAP
    base = 'c302_v2'
    data = {
        'c302_v2': {
            'path': f'/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks_base-A_v2/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z0p950/MAP_QSO_pypower_poles.npy', 
            'label': 'fNL=100, base-A, v2', 
            'color': 'black', 
            'lstyle': '-',
            'alpha': 1,
        },
    }
    data, k_1st = load_poles_data(data)
    ### sampled HOD mocks
    data = load_sampled_HOD_mocks(data, k_1st=k_1st, num=num)
    ### EZmocks loading
    if dirEZmocks is not None:
        p0_ez, p0_ez_avg, p0_err = load_EZmocks(dirEZmocks)
    
    ### define base
    if base in data.keys():
        P0_base = data[base]['p0']
    else:
        raise ValueError(f"Unknown base: {base}")

    ### plot
    fig, axs = plt.subplots(2,1,constrained_layout=True,sharex='col',figsize=(8,8),gridspec_kw={'height_ratios': [3, 1]})
    # P0_base = p0_ez_avg if dirEZmocks is not None else P0_base # for test
    if dirEZmocks is not None:
        # top panel: EZmocks
        p = p0_ez[0]
        axs[0].plot(k_1st[1:], p[1:], color='gray', alpha=0.3, label='EZmock')
        for p in p0_ez[1:]:
            axs[0].plot(k_1st[1:], p[1:], color='gray', alpha=0.3)
        axs[0].plot(k_1st[1:], p0_ez_avg[1:], color='gray', lw=2, label='EZmock average')
        # bottom panel: EZmocks fractional errors
        frac_ez = p0_ez_avg / P0_base - 1
        frac_err = p0_err / P0_base 
        axs[1].plot(k_1st[1:], frac_ez[1:], color='gray', lw=2)
        axs[1].fill_between(k_1st[1:], - frac_err[1:], frac_err[1:], color='gray', alpha=0.5, label=r'EZmock $1\sigma$')    
    # top panel: original spectra
    for key in data.keys():
        p0 = data[key]['p0']
        axs[0].plot(k_1st[1:], p0[1:], label=data[key]['label'], color=data[key]['color'], linestyle=data[key]['lstyle'], alpha=data[key]['alpha'])
    axs[0].set_xscale('log')
    axs[0].set_yscale('log')
    axs[0].set_ylabel(r'$P_0(k)$ [$(\mathrm{Mpc}/h)^{3}$]')
    axs[0].legend()
    # bottom panel: fractional errors (P_variant - P_base) / P_base
    for key in data.keys():
        p0 = data[key]['p0']
        frac = p0 / P0_base - 1
        axs[1].plot(k_1st[1:], frac[1:], color=data[key]['color'], linestyle=data[key]['lstyle'], alpha=data[key]['alpha'])
    axs[1].set_xscale('log')
    axs[1].set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
    axs[1].set_ylabel(r'$P^{\rm xx}/P^{\rm base}-1$')
    ylim=0.3
    axs[1].set_ylim(-ylim, ylim)
    axs[1].legend()
    plt.tight_layout()
    fn = WORK_DIR + f'/mock_ps.png'
    plt.savefig(fn, dpi=300)
    print(f'Saved figure to {fn}')
