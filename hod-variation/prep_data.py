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

outdir='../data/for_hod/v2_rp6s11/'
## rp/s bin midpoints saved to data files
rpbins=np.geomspace(0.01,100,25)
print('x bins:', rpbins)
rpbinsmid=(rpbins[1:]+rpbins[:-1])/2


## QSO

## arocher's meas
y3rppidir='/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v2/PIP/cosmo_0/rppi/'
y3smudir='/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v2/PIP/cosmo_0/smu/'
qso_bins = {'z1': (0.8, 1.1), 'z2': (1.1, 1.4), 'z3': (1.4, 1.7)}

## hanyu's meas
# y3rppidir='/pscratch/sd/h/hanyuz/measurements_smallscale/rppi/'
# y3smudir='/pscratch/sd/h/hanyuz/measurements_smallscale/smu/'
# qso_bins = {'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}

# idx_min_rp = 3
idx_min_rp = 6
idx_max_rp = 21
# idx_min_s  = 8
idx_min_s  = 11
idx_max_s  = 21

wpqso = {}
xiqso = {}
for tag, (zmin, zmax) in qso_bins.items():
    fname = f"allcounts_QSO_GCcomb_{zmin:.1f}_{zmax:.1f}_pip_angular_bitwise_log_njack128_nran4_split20.npy"
    wpqso[tag] = readwp(y3rppidir + fname)
    xiqso[tag] = readxi02(y3smudir + fname)

## get jackknife covariance
idx_wp_cut   = np.arange(idx_min_rp, idx_max_rp)  
idx_xi_cut  = np.arange(idx_min_s, idx_max_s)
idx_xi02_cut = np.concatenate((idx_xi_cut, idx_xi_cut + 24))  
covqso = {}
for tag in qso_bins:
    covqso[tag] = get_combined_jkcov(wpqso[tag][3], xiqso[tag][3], idx_wp_cut, idx_xi02_cut)

## save wp cut
for tag, (zmin, zmax) in qso_bins.items():
    np.savetxt(outdir+f"wp_QSO_{zmin:.1f}_{zmax:.1f}_cut.dat",
               np.column_stack((rpbinsmid[idx_wp_cut],
                                wpqso[tag][0][idx_wp_cut],
                                wpqso[tag][2][idx_wp_cut])))
## save xi02 cut
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

QSO_nz_NGC=np.loadtxt('/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/v2/PIP/QSO_NGC_nz.txt',skiprows=2)
QSO_nz_SGC=np.loadtxt('/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/v2/PIP/QSO_SGC_nz.txt',skiprows=2)

nzqso={}
for tag, (zmin, zmax) in qso_bins.items():
    z_idx=np.where((QSO_nz_NGC[:,0]>=zmin) & (QSO_nz_NGC[:,0]<zmax))[0]
    nzqso[tag]=nz_comb(QSO_nz_NGC,QSO_nz_SGC,z_idx)

    # zeff = compute_zeff('/dvs_ro/cfs/cdirs/desi/survey/catalogs/Y3/LSS/loa-v1/LSScats/v2/PIP/QSO_clustering.dat.fits',zrange=[zmin, zmax])
    zeff = 'No FKP weight now, no zeff.'
    print(tag, zmin,'-', zmax, 'zeff:', zeff)
print(nzqso)
