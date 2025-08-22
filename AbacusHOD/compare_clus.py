#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a script for compare the wp, xi0 and xi2 between the MAP mock and the observation data.

Usage
-----
$ python ./compare_clus.py --help
"""

import numpy as np
import h5py
import argparse
import yaml
from matplotlib import pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')

DEFAULTS = {}
DEFAULTS['path2config'] = 'config/lrg_z0_test_map.yaml'

def load_mock_clustering(dir):
    wp = np.loadtxt(f'{dir}/wp_LRG.txt')
    xi0 = np.loadtxt(f'{dir}/xi0_LRG.txt')
    xi2 = np.loadtxt(f'{dir}/xi2_LRG.txt')
    return wp, xi0, xi2

def plot_wp(rp, wp, wp_err, wp_mock, path2wp):
    plt.clf()
    fig, axs = plt.subplots(2, 1, figsize=(7, 7), sharex=True, gridspec_kw={'height_ratios': [3, 2], 'hspace': 0})
    ### up panel
    axs[0].errorbar(rp, rp*wp, yerr=rp*wp_err, fmt='o', label='hdf5', mfc='none', color='C0')
    axs[0].plot(rp, rp*wp_mock, label='mock', color='C1')
    axs[0].set_ylabel(r'$r_p w_p [({\rm Mpc}/h)^{-2}]$')
    axs[0].set_xscale('log')
    axs[0].legend()
    ### low panel
    axs[1].fill_between(rp, -wp_err/wp, wp_err/wp, color='gray', alpha=0.5, label=r'$\pm 1\sigma$, hdf5')
    axs[1].plot(rp, (wp_mock - wp)/wp, label='mock', color='C1')
    axs[1].axhline(0, ls='--', color='gray')
    axs[1].set_xscale('log')
    axs[1].set_xlabel(r'$r_p [{\rm Mpc}/h]$')
    axs[1].set_ylabel(r'$\Delta w_p/w_p^{\rm obs}$')
    plt.tight_layout()
    plt.legend()
    plt.savefig(path2wp)

def plot_xi0(s, xi0, xi0_err, xi0_mock, path2xi0):
    plt.clf()
    fig, axs = plt.subplots(2, 1, figsize=(7, 7), sharex=True, gridspec_kw={'height_ratios': [3, 2], 'hspace': 0})
    ### up panel    
    axs[0].errorbar(s, s*xi0, yerr=s*xi0_err, fmt='o', label='hdf5', mfc='none', color='C0')
    axs[0].plot(s, s*xi0_mock, label='mock', color='C1')
    axs[0].set_ylabel(r'$s \xi_0 [({\rm Mpc}/h)^{-2}]$')
    axs[0].set_xscale('log')
    axs[0].legend()
    ### low panel
    axs[1].fill_between(s, -xi0_err/xi0, xi0_err/xi0, color='gray', alpha=0.5, label=r'$\pm 1\sigma$, hdf5')
    axs[1].plot(s, (xi0_mock - xi0)/xi0, label='mock', color='C1')
    axs[1].axhline(0, ls='--', color='gray')
    axs[1].set_xscale('log')
    axs[1].set_xlabel(r'$s [{\rm Mpc}/h]$')
    axs[1].set_ylabel(r'$\Delta \xi_0 / \xi_0^{\rm obs}$')
    plt.tight_layout()
    plt.legend()
    plt.savefig(path2xi0)
    
def plot_xi2(s, xi2, xi2_err, xi2_mock, path2xi2):
    plt.clf()
    fig, axs = plt.subplots(2, 1, figsize=(7, 7), sharex=True, gridspec_kw={'height_ratios': [3, 2], 'hspace': 0})
    ### up panel    
    axs[0].errorbar(s, s*xi2, yerr=s*xi2_err, fmt='o', label='hdf5', mfc='none', color='C0')
    axs[0].plot(s, s*xi2_mock, label='mock', color='C1')
    axs[0].set_ylabel(r'$s \xi_2 [({\rm Mpc}/h)^{-2}]$')
    axs[0].set_xscale('log')
    axs[0].legend()
    ### low panel
    axs[1].fill_between(s, -xi2_err/xi2, xi2_err/xi2, color='gray', alpha=0.5, label=r'$\pm 1\sigma$, hdf5')
    axs[1].plot(s, (xi2_mock - xi2)/xi2, label='mock', color='C1')
    axs[1].axhline(0, ls='--', color='gray')
    axs[1].set_xscale('log')
    axs[1].set_xlabel(r'$s [{\rm Mpc}/h]$')
    axs[1].set_ylabel(r'$\Delta \xi_2 / \xi_2^{\rm obs}$')
    plt.tight_layout()
    plt.legend()
    plt.savefig(path2xi2)

def main(path2config):
    config = yaml.safe_load(open(path2config))
    data_params = config['data_params']
    path2data = data_params['tracer_combos']['LRG_LRG']['path2data']
    z='z0'  # assuming the data is for redshift z0=0.5 (0.4-0.6), change as needed
    mock_dir = config['sim_params']['output_dir']
    plots_params = config['clustering_plots']
    path2wp = plots_params['path2wp']
    path2xi0 = plots_params['path2xi0']
    path2xi2 = plots_params['path2xi2']
    
    ## reference data
    with h5py.File(path2data, 'r') as f:
        group = f[z]
        data_vector = group['data_vector'][:]
        cov = group['cov'][:]
        rp = group['rp'][:]
        s = group['s'][:]
        redshift_range = group.attrs['redshift_range']
    print(redshift_range)
    wp = data_vector[:18]
    xi0 = data_vector[18:31]
    xi2 = data_vector[31:44]
    
    ## mock clustering
    wp_mock, xi0_mock, xi2_mock = load_mock_clustering(mock_dir)
    
    ## plots
    wp_err = np.sqrt(np.diag(cov))[:18]
    plot_wp(rp, wp, wp_err, wp_mock, path2wp)
    xi0_err = np.sqrt(np.diag(cov))[18:31]
    plot_xi0(s, xi0, xi0_err, xi0_mock, path2xi0)
    xi2_err = np.sqrt(np.diag(cov))[31:44]
    plot_xi2(s, xi2, xi2_err, xi2_mock, path2xi2)


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
        '--path2config', help='Path to the config file', default=DEFAULTS['path2config']
    )
    args = vars(parser.parse_args())
    main(**args)