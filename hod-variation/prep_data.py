#!/usr/bin/env python
# coding: utf-8

"""
This is a script for preparing the data used in HOD fitting.

Credit: https://github.com/ahnyu/hod-variation/blob/main/prep_data_v1.1.ipynb , modified by Siyi Zhao

Usage
-----
$ source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
$ python prep_data.py 
"""

import numpy as np
import os
import sys
current_dir = os.getcwd()
source_dir = os.path.join(current_dir,"source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from loading_helpers import readwp, readxi02, get_combined_jkcov, cov2corr, nz_comb, compute_zeff

outdir='../data/for_hod/v1.1/'
## rp/s bin midpoints saved to data files
rpbins=np.geomspace(0.01,100,25)
rpbinsmid=(rpbins[1:]+rpbins[:-1])/2


## QSO

## arocher's meas
# y3rppidir='/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v1.1/PIP/cosmo_0/rppi/'
# y3smudir='/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v1.1/PIP/cosmo_0/smu/'
# qso_bins = {'z0': (0.8, 2.1), 'z1': (0.8, 1.1), 'z2': (1.1, 1.4), 'z3': (1.4, 1.7)}

## hanyu's meas
y3rppidir='/pscratch/sd/h/hanyuz/measurements_smallscale/rppi/'
y3smudir='/pscratch/sd/h/hanyuz/measurements_smallscale/smu/'
qso_bins = {'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}

wpqso = {}
xiqso = {}
for tag, (zmin, zmax) in qso_bins.items():
    fname = f"allcounts_QSO_GCcomb_{zmin:.1f}_{zmax:.1f}_pip_angular_bitwise_log_njack128_nran4_split20.npy"
    wpqso[tag] = readwp(y3rppidir + fname)
    xiqso[tag] = readxi02(y3smudir + fname)

## get jackknife covariance
idxwp_qso   = np.arange(3, 21)
idxxi02_qso = np.concatenate((np.arange(8, 21), np.arange(8 + 24, 21 + 24)))
covqso = {}
for tag in qso_bins:
    covqso[tag] = get_combined_jkcov(wpqso[tag][3], xiqso[tag][3], idxwp_qso, idxxi02_qso)

## save wp cut
idx_wp_cut = np.arange(3, 21)
for tag, (zmin, zmax) in qso_bins.items():
    np.savetxt(outdir+f"wp_QSO_{zmin:.1f}_{zmax:.1f}_cut.dat",
               np.column_stack((rpbinsmid[idx_wp_cut],
                                wpqso[tag][0][idx_wp_cut],
                                wpqso[tag][2][idx_wp_cut])))
## save xi02 cut
idx_xi_cut = np.arange(8, 21)
for tag, (zmin, zmax) in qso_bins.items():
    np.savetxt(outdir+f"xi02_QSO_{zmin:.1f}_{zmax:.1f}_cut.dat",
               np.column_stack((rpbinsmid[idx_xi_cut],
                                xiqso[tag][0][0][idx_xi_cut],       
                                xiqso[tag][2][idx_xi_cut],          
                                xiqso[tag][0][1][idx_xi_cut],       
                                xiqso[tag][2][idx_xi_cut + 24])))   
## save cov cut
for tag, (zmin, zmax) in qso_bins.items():
    np.savetxt(outdir+f"cov_QSO_{zmin:.1f}_{zmax:.1f}_cut.dat", covqso[tag])


## n(z) for QSO

QSO_nz_NGC=np.loadtxt('/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/v1.1/PIP/QSO_NGC_nz.txt',skiprows=2)
QSO_nz_SGC=np.loadtxt('/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/v1.1/PIP/QSO_SGC_nz.txt',skiprows=2)

nzqso={}
for tag, (zmin, zmax) in qso_bins.items():
    z_idx=np.where((QSO_nz_NGC[:,0]>=zmin) & (QSO_nz_NGC[:,0]<zmax))[0]
    nzqso[tag]=nz_comb(QSO_nz_NGC,QSO_nz_SGC,z_idx)

    zeff = compute_zeff('/dvs_ro/cfs/cdirs/desi/survey/catalogs/Y3/LSS/loa-v1/LSScats/v1.1/PIP/QSO_clustering.dat.fits',zrange=[zmin, zmax])
    print(tag, zmin,'-', zmax, 'zeff:', zeff)
print(nzqso)
