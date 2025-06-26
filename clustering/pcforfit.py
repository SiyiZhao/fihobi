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

def main(dir, fix, check):
    pycorr_out_path = dir + f'/smu/allcounts_{fix}.npy'

    ## define s edges and log midpoints
    # sedges = np.geomspace(0.01, 30., 41)
    # s_log_mid = 10**((np.log10(sedges[:-1]) + np.log10(sedges[1:])) / 2)

    ## load the TwoPointCorrelationFunction result
    result = TwoPointCorrelationFunction.load(pycorr_out_path)
    sep, corr, cov = result.get_corr(mode='poles', return_sep=True, return_cov=True)
    num = sep.shape[0]
    xi0 = corr[0, :]
    xi2 = corr[1, :]

    cov00 = cov[:num, :num]
    
    ## cut the nan part
    mask = ~np.isnan(xi0)
    sep_sel = sep[mask]
    xi0_sel = xi0[mask]
    xi2_sel = xi2[mask]
    cov00_sel = cov00[mask][:, mask]
    if np.isnan(cov00_sel).any():
        print("Warning: cov00_sel contains NaN values.")

    ## save 
    np.savetxt(dir + f'/hodfit/xipoles_{fix}.txt', np.column_stack((sep_sel, xi0_sel, xi2_sel)), header='sep xi0 xi2')
    np.save(dir + f'/hodfit/cov_xi0_{fix}.npy', cov00_sel)

    ## check the xi0 and std with .txt file
    if check==True:
        xi0_std = np.sqrt(np.diag(cov00))
        ref = np.loadtxt(dir + '/smu/xipoles_LRG_GCcomb_0.6_0.8_pip_angular_bitwise_log1_njack128_nran4_split20.txt')
        savg = ref[:, 1]
        corr0 = ref[:, 2]
        std0 = ref[:, 5]
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
                    diff = np.abs(arr1[mask] - arr2[mask])
                    print(f"Max difference: {diff.max()} at index {diff.argmax()}")

        check_and_report(savg, sep, "savg", "sep")
        check_and_report(corr0, xi0, "corr0", "xi0")
        check_and_report(std0, xi0_std, "std0", "xi0_std")


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
        '--check', action='store_true',
        help='Check the output against the text file outputed by pycorr'
    )
    args = vars(parser.parse_args())
    main(**args)
