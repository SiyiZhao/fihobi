# !/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Measure galaxy bias from mock power spectrum.

- the workdir is ~/projects/fihobi/mock-data-cov/
- pypower requires `source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main` on NERSC

Usage:
    python mock_bias.py --tag z1
'''

import argparse
import numpy as np
from pypower import PowerSpectrumMultipoles

def parse_args():
    parser = argparse.ArgumentParser(description=argparse.SUPPRESS)
    parser.add_argument('--tag', type=str, required=True, help='Tag for the mock (e.g., z1, z2, etc.)')
    return parser.parse_args()

## Read the pypower
def read_pypower(fn):
    poles = PowerSpectrumMultipoles.load(fn)
    k, p0 = poles(ell=0, return_k=True, complex=False)
    k = k[1:]
    p0 = p0[1:]
    return k, p0

## linear power spectrum at z 

def read_class_ini(IDIR):
    import re
    p = {}
    fname = IDIR + "CLASS.ini"
    try:
        with open(fname) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = map(str.strip, line.split('=', 1))
                    # 只保留字母數字與下劃線的 key
                    key = re.sub(r'[^A-Za-z0-9_]', '', key)
                    try:
                        p[key] = float(val.split()[0])
                    except:
                        pass
    except Exception as e:
        print("Cannot read CLASS.ini:", e)
    return p

def load_Abacus_cosmology_params(IDIR):
    params = read_class_ini(IDIR)
    h = params['h']
    Omega_m = (params["omega_b"] + params["omega_cdm"]) / (h**2)
    Omega_L = 1.0 - Omega_m  # assume flat
    return Omega_m, Omega_L

def load_Abacus_linear_power(IDIR):
    data = np.loadtxt(IDIR+"CLASS_power")
    klin = data[:,0]
    plin_z1 = data[:,1]
    return klin, plin_z1


def grow_plin(z_out, plin_in, IDIR = "/global/homes/s/siyizhao/lib/AbacusSummit/Cosmologies/abacus_cosm000/", z_in=1.0):
    from scipy.integrate import solve_ivp

    a_init = 1e-4
    y0 = [a_init, 1.0]  # D(a_init)=a_init, D'(a_init)=1 (因 D~a)
    # ODE for D(a): y = [D, dD/da]
    def deriv(a, y):
        D, dDda = y
        Om, Ol = load_Abacus_cosmology_params(IDIR)
        E2 = Om / a**3 + Ol
        H = np.sqrt(E2)
        # d ln H / da = (-3 Om)/(2 a (Om + Ol a^3))
        dlnHda = -1.5 * Om / (a * (Om + Ol * a**3))
        coef = (3.0 / a) + dlnHda
        term = 1.5 * Om / (a**2 * (Om + Ol * a**3))
        ddDda = -coef * dDda + term * D
        return [dDda, ddDda]

    sol = solve_ivp(deriv, (a_init, 1.0), y0, dense_output=True, rtol=1e-6, atol=1e-9)

    
    a_out = 1.0 / (1.0 + z_out)
    a_in = 1.0 / (1.0 + z_in)  # z_in=1
    D_out = sol.sol(a_out)[0]
    D_in = sol.sol(a_in)[0]
    growth_ratio = D_out / D_in  # D(z_out)/D(z=0) with D(z=0)=1
    plin_out = plin_in * (growth_ratio**2)
    return plin_out

## linear bias

def measure_bias_k(k, P0, klin, plin):
    # valid points: remove NaNs and restrict to k range covered by klin
    mask = (~np.isnan(k)) & (~np.isnan(P0))
    mask &= (k >= klin.min()) & (k <= klin.max())
    k_cut = k[mask] 
    p0_cut = P0[mask]
    # interpolate in log-log space to preserve power-law behavior
    ln_klin = np.log(klin)
    ln_plin = np.log(plin)
    ln_kcut = np.log(k_cut)
    ln_plin_interp = np.interp(ln_kcut, ln_klin, ln_plin)
    plin_interp = np.exp(ln_plin_interp)
    bk = np.sqrt(p0_cut / plin_interp)
    return k_cut, bk

def average_bias(k, bk, bkmin=0.001, bkmax=0.15):
    bmask = (k >= bkmin) & (k <= bkmax)
    bias = np.mean(bk[bmask])
    return bias

def plot_bias(k, bk, bias, bkmin, bkmax, fn=None):
    from matplotlib import pyplot as plt
    plt.figure(figsize=(6,4))
    plt.plot(k, bk, marker='o', linestyle='-', markersize=4)
    plt.hlines(y=bias, xmin=bkmin, xmax=bkmax, color='r', linestyle='--', label=f'Mean bias={bias:.3f} in [{bkmin}, {bkmax}]') 
    # plt.xscale('log')
    plt.xlabel('k [h/Mpc]')
    plt.ylabel('b')
    plt.tight_layout()
    plt.legend()
    if fn is not None:
        plt.savefig(fn)
        print(f"Bias plot saved to {fn}")
    else:
        plt.show()

if __name__ == "__main__":
    bkmin = 0.05
    bkmax = 0.15
    IDIR = "/global/homes/s/siyizhao/lib/AbacusSummit/Cosmologies/abacus_cosm000/"
    args = parse_args()
    tag = args.tag
    # hod_model = ''
    hod_model = '_base-A-dv'
    fn_out = f'out/mock_bias_{tag}{hod_model}.png'
    
    z_mock = {'z1': 0.95, 'z2': 1.25, 'z3': 1.55, 'z4': 2.0, 'z5': 2.5, 'z6': 3.0}
    z = z_mock[tag]
    path2dir=f'/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks{hod_model}/Abacus_pngbase_c302_ph000/z{z:.3f}/galaxies_rsd_dv/'

    k_mock, P0_mock = read_pypower(path2dir + 'pypower_poles.npy')
    klin, plin_z1 = load_Abacus_linear_power(IDIR)
    plin_z = grow_plin(z, plin_z1, z_in=1.0)
    k_plot, bk = measure_bias_k(k_mock, P0_mock, klin, plin_z)
    bias = average_bias(k_plot, bk, bkmin=bkmin, bkmax=bkmax)
    plot_bias(k_plot, bk, bias, bkmin, bkmax, fn=fn_out)
    print(f"Measured bias for {tag} (z={z}): {bias:.4f}")
    np.savetxt(path2dir + f'mock_bias.txt', [bias])
    print(f"Bias value saved to {path2dir + f'mock_bias.txt'}")
    