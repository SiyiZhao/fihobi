#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script reads the TwoPointCorrelationFunction output from pycorr and saves the data along with the covariance matrix for HOD fitting.

Usage
-----
$ python pcforfit.py --help
"""

import argparse
import numpy as np
from pycorr import TwoPointCorrelationFunction

DEFAULTS = {}
DEFAULTS['dir'] = '/global/homes/s/siyizhao/data/Y3/loa-v1'
DEFAULTS['fix'] = 'LRG_GCcomb_0.6_0.8_pip_angular_bitwise_log_njack128_nran4_split20'
DEFAULTS['mode'] = 'smu'  # Default mode is 'smu' for multipoles

def check_and_report(arr1, arr2, name1, name2):
    if np.allclose(arr1, arr2):
        print(f"{name1} and {name2} match.")
    else:
        # Ignore positions where either array has nan
        mask = ~np.isnan(arr1) & ~np.isnan(arr2)
        if np.allclose(arr1[mask], arr2[mask]):
            print(f"{name1} and {name2} match (ignoring NaNs).")
        else:
            print(f"{name1} and {name2} do NOT match (ignoring NaNs).")
            diff = np.abs((arr1[mask] - arr2[mask]) / arr2[mask])
            print(f"Max difference fraction: {diff.max()} at index {diff.argmax()}")

def pcforfit_poles(dir, fix, check=False):
    pycorr_out_path = dir + f'/smu/allcounts_{fix}.npy'

    ## load the TwoPointCorrelationFunction result
    result = TwoPointCorrelationFunction.load(pycorr_out_path)

    sep, corr, cov = result.get_corr(mode='poles', return_sep=True, return_cov=True)
    num = sep.shape[0]
    xi0 = corr[0, :]
    xi2 = corr[1, :]
    cov00 = cov[:num, :num]
    cov22 = cov[num:2*num, num:2*num]
    cov02 = cov[:num, num:2*num]
    cov20 = cov[num:2*num, :num]
    
    ## cut the nan part
    mask = ~np.isnan(xi0)
    sep_sel = sep[mask]
    xi0_sel = xi0[mask]
    xi2_sel = xi2[mask]
    cov00_sel = cov00[mask][:, mask]
    cov22_sel = cov22[mask][:, mask]  
    cov02_sel = cov02[mask][:, mask]
    cov20_sel = cov20[mask][:, mask]
    cov0022 = np.block([[cov00_sel, cov02_sel],
                        [cov20_sel, cov22_sel]])
    if np.isnan(cov00_sel).any():
        print("Warning: cov00_sel contains NaN values.")
    if np.isnan(cov22_sel).any():
        print("Warning: cov22_sel contains NaN values.")
    if np.isnan(cov02_sel).any():
        print("Warning: cov02_sel contains NaN values.")
    if np.isnan(cov20_sel).any():
        print("Warning: cov20_sel contains NaN values.")

    ## save 
    np.savetxt(dir + f'/hodfit/xipoles_{fix}.dat', np.column_stack((sep_sel, xi0_sel, xi2_sel)), header='sep xi0 xi2')
    np.save(dir + f'/hodfit/cov_xi02_{fix}.npy', cov0022)
    np.save(dir + f'/hodfit/cov_xi0_{fix}.dat', cov00_sel)
    np.save(dir + f'/hodfit/cov_xi2_{fix}.dat', cov22_sel)

    ## check the xi0 and std with .txt file
    if check==True:
        xi0_std = np.sqrt(np.diag(cov00))
        xi2_std = np.sqrt(np.diag(cov22))
        if 'log' in fix:
            fix1 = fix.replace('log', 'log1')
        elif 'lin' in fix:
            fix1 = fix.replace('lin', 'lin1')
        else:
            fix1 = fix
        ref = np.loadtxt(dir + f'/smu/xipoles_{fix1}.txt')
        savg = ref[:, 1]
        corr0 = ref[:, 2]
        corr2 = ref[:, 3]
        std0 = ref[:, 5]
        std2 = ref[:, 6]

        check_and_report(savg, sep, "savg", "sep")
        check_and_report(corr0, xi0, "corr0", "xi0")
        check_and_report(std0, xi0_std, "std0", "xi0_std")
        check_and_report(corr2, xi2, "corr2", "xi2")
        check_and_report(std2, xi2_std, "std2", "cov22_std")

def pcforfit_wp(dir, fix, check=False):
    pycorr_out_path = dir + f'/rppi/allcounts_{fix}.npy'
    result = TwoPointCorrelationFunction.load(pycorr_out_path)
    sep, corr, cov = result.get_corr(mode='wp', return_sep=True, return_cov=True)
    
    mask = (sep >= 0.1) & (sep <= 30.0)
    rp = sep[mask]
    wp = corr[mask]
    cov_wp = cov[mask][:, mask]
    ## save
    np.savetxt(dir + f'/hodfit/wp_{fix}.dat', np.column_stack((rp, wp)), header='rp wp')
    np.savetxt(dir + f'/hodfit/cov_wp_{fix}.dat', cov_wp)
    
    if check:
        if 'log' in fix:
            fix1 = fix.replace('log', 'log1')
        elif 'lin' in fix:
            fix1 = fix.replace('lin', 'lin1')
        else:
            fix1 = fix
        ref = np.loadtxt(dir + f'/rppi/wp_{fix1}.txt')
        rpavg = ref[:, 1]
        corr_wp = ref[:, 2]
        std_wp = ref[:, 3]

        check_and_report(rpavg, sep, "rpavg", "sep")
        check_and_report(corr_wp, corr, "corr_wp", "corr")
        cov_std = np.sqrt(np.diag(cov))
        check_and_report(std_wp, cov_std, "std_wp", "cov_std")

def pcforfit_poles_wp(dir, fix, check=False):
    pycorr_out_path = dir + f'/smu/allcounts_{fix}.npy'

    ## load the TwoPointCorrelationFunction result
    result = TwoPointCorrelationFunction.load(pycorr_out_path)

    sep, corr, cov = result.get_corr(mode='poles', return_sep=True, return_cov=True)
    num = sep.shape[0]
    xi0 = corr[0, :]
    xi2 = corr[1, :]
    cov00 = cov[:num, :num]
    cov22 = cov[num:2*num, num:2*num]
    cov02 = cov[:num, num:2*num]
    cov20 = cov[num:2*num, :num]
    
    ## cut the nan part
    mask = ~np.isnan(xi0)
    sep_sel = sep[mask]
    xi0_sel = xi0[mask]
    xi2_sel = xi2[mask]
    cov00_sel = cov00[mask][:, mask]
    cov22_sel = cov22[mask][:, mask]  
    cov02_sel = cov02[mask][:, mask]
    cov20_sel = cov20[mask][:, mask]
    cov0022 = np.block([[cov00_sel, cov02_sel],
                        [cov20_sel, cov22_sel]])
    
    

def main(dir, fix, mode, check):
    
    ## define s edges and log midpoints
    # sedges = np.geomspace(0.01, 30., 41)
    # s_log_mid = 10**((np.log10(sedges[:-1]) + np.log10(sedges[1:])) / 2)

    if mode=='smu':
        pcforfit_poles(dir, fix, check)
    elif mode=='wp':
        pcforfit_wp(dir, fix, check)
    elif mode=='wp+smu':
        pcforfit_poles_wp(dir, fix, check)
    else:
        raise ValueError("Unsupported mode. Use 'smu' 'wp' or 'wp+smu'.")


class ArgParseFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass

if __name__ == '__main__':
    # parsing arguments
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=ArgParseFormatter
    )
    parser.add_argument(
        '--dir', help='Path to the data directory', default=DEFAULTS['dir']
    )
    parser.add_argument(
        '--fix', help='Fix string for the output files', default=DEFAULTS['fix']
    )
    parser.add_argument(
        '--mode', choices=['smu', 'wp', 'wp+smu'], default=DEFAULTS['mode'],
        help='Mode of the two-point correlation function: smu for multipoles, wp for projected correlation function, wp+smu for combining both.'
    )
    parser.add_argument(
        '--check', action='store_true',
        help='Check the output against the text file outputed by pycorr'
    )
    args = vars(parser.parse_args())
    main(**args)
