#!/usr/bin/env python
# coding: utf-8

"""
This is a script for preparing the data used in HOD fitting.

Usage
-----
$ source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
$ python prep_data.py 

Author: Siyi Zhao
Refer to: https://github.com/ahnyu/hod-variation/blob/main/prep_data_v1.1.ipynb 
"""

import numpy as np
import os
import sys
current_dir = os.getcwd()
source_dir = os.path.join(current_dir,"source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from loading_helpers import readwp, readxi02, get_combined_jkcov, cov2corr, nz_comb, compute_zeff

# data_version, output and x bins ---------------------------------------------------

# data_version='v1.1'  # loa-v1 v1.1
data_version='v2'  # loa-v1 v2
outdir=f'../data/for_hod/{data_version}_rp6s11/'

## rp/s bin midpoints saved to data files
rpbins=np.geomspace(0.01,100,25)
print('x bins:', rpbins)
rpbinsmid=(rpbins[1:]+rpbins[:-1])/2

# idx_min_rp = 3
idx_min_rp = 6
idx_max_rp = 21
# idx_min_s  = 8
idx_min_s  = 11
idx_max_s  = 21

### Data -----------------------------------------------------------------------

## arocher's meas
y3rppidir=f'/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/{data_version}/PIP/cosmo_0/rppi/'
y3smudir=f'/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/{data_version}/PIP/cosmo_0/smu/'
y3nzdir=f'/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/{data_version}/PIP/'
y3catdir=f'/dvs_ro/cfs/cdirs/desi/survey/catalogs/Y3/LSS/loa-v1/LSScats/{data_version}/PIP/'
zbins = {
    'LRG': {'z1': (0.4, 0.6), 'z2': (0.6, 0.8), 'z3': (0.8, 1.1)},
    'QSO': {'z1': (0.8, 1.1), 'z2': (1.1, 1.4), 'z3': (1.4, 1.7)},
    'highz-QSO': {'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}
}

### Functions ------------------------------------------------------------------

def save_data(tracer, y3rppidir=y3rppidir, y3smudir=y3smudir):
    ''' save data for a given tracer 
    tracer: 'LRG', 'QSO', 'highz-QSO'
    '''
    t_zbins = zbins[tracer]
    if tracer == 'highz-QSO':
        tracer = 'QSO'  # folder name uses 'QSO' for highz-QSO
    wp = {}
    xi = {}
    for tag, (zmin, zmax) in t_zbins.items():
        fname = f"allcounts_{tracer}_GCcomb_{zmin:.1f}_{zmax:.1f}_pip_angular_bitwise_log_njack128_nran4_split20.npy"
        wp[tag] = readwp(y3rppidir + fname)
        xi[tag] = readxi02(y3smudir + fname)

    ## get jackknife covariance
    idx_wp_cut   = np.arange(idx_min_rp, idx_max_rp)  
    idx_xi_cut  = np.arange(idx_min_s, idx_max_s)
    idx_xi02_cut = np.concatenate((idx_xi_cut, idx_xi_cut + 24))  
    cov = {}
    for tag in t_zbins:
        cov[tag] = get_combined_jkcov(wp[tag][3], xi[tag][3], idx_wp_cut, idx_xi02_cut)

    ## save wp cut
    for tag, (zmin, zmax) in t_zbins.items():
        np.savetxt(outdir+f"wp_{tracer}_{zmin:.1f}_{zmax:.1f}_cut.dat",
                np.column_stack((rpbinsmid[idx_wp_cut],
                                    wp[tag][0][idx_wp_cut],
                                    wp[tag][2][idx_wp_cut])))
    ## save xi02 cut
    for tag, (zmin, zmax) in t_zbins.items():
        np.savetxt(outdir+f"xi02_{tracer}_{zmin:.1f}_{zmax:.1f}_cut.dat",
                np.column_stack((rpbinsmid[idx_xi_cut],
                                    xi[tag][0][0][idx_xi_cut],       
                                    xi[tag][2][idx_xi_cut],          
                                    xi[tag][0][1][idx_xi_cut],       
                                    xi[tag][2][idx_xi_cut + 24])))   
    ## save cov cut
    for tag, (zmin, zmax) in t_zbins.items():
        np.savetxt(outdir+f"cov_{tracer}_{zmin:.1f}_{zmax:.1f}_cut.dat", cov[tag])



def load_nz(tracer):
    ''' load n(z) for a given tracer 
    tracer: 'LRG', 'QSO', 'highz-QSO'
    '''
    t_zbins = zbins[tracer]
    if tracer == 'highz-QSO':
        tracer = 'QSO'  # folder name uses 'QSO' for highz-QSO
    ## Read n(z) for NGC and SGC
    nz_NGC=np.loadtxt(y3nzdir+f'{tracer}_NGC_nz.txt',skiprows=2)
    nz_SGC=np.loadtxt(y3nzdir+f'{tracer}_SGC_nz.txt',skiprows=2)
    ## combine NGC and SGC
    nz_data = {}
    for tag, (zmin, zmax) in t_zbins.items():
        z_idx=np.where((nz_NGC[:,0]>=zmin) & (nz_NGC[:,0]<zmax))[0]
        nz_data[tag]=nz_comb(nz_NGC,nz_SGC,z_idx)
    return nz_data

def show_zeff(tracer, data_version='v1.1'):
    ''' measure zeff for a given tracer 
    tracer: 'LRG', 'QSO', 'highz-QSO'
    '''
    t_zbins = zbins[tracer]
    if tracer == 'highz-QSO':
        tracer = 'QSO'  # folder name uses 'QSO' for highz-QSO
    zeff_data = {}
    if data_version=='v1.1':
        for tag, (zmin, zmax) in t_zbins.items():
            zeff = compute_zeff(y3catdir+f'{tracer}_clustering.dat.fits',zrange=[zmin, zmax])
            zeff_data[tag] = zeff
            print(tag, zmin,'-', zmax, 'zeff:', zeff)
    elif data_version=='v2':
        for tag, (zmin, zmax) in t_zbins.items():
            zeff_NGC = compute_zeff(y3catdir+f'{tracer}_NGC_clustering.dat.fits',zrange=[zmin, zmax])
            zeff_SGC = compute_zeff(y3catdir+f'{tracer}_SGC_clustering.dat.fits',zrange=[zmin, zmax])
            zeff_data[tag] = (zeff_NGC, zeff_SGC)
            print(tag, zmin,'-', zmax, 'zeff of NGC:', zeff_NGC, ', zeff of SGC:', zeff_SGC)
    return zeff_data

### Usage Example --------------------------------------------------------------

if __name__ == "__main__":
    # tracer='QSO'
    tracer='highz-QSO' 
    # tracer='LRG'
    
    if tracer=='highz-QSO':
        ## hanyu's meas
        if data_version=='v1.1':
            y3rppidir='/pscratch/sd/h/hanyuz/measurements_smallscale/rppi/'
            y3smudir='/pscratch/sd/h/hanyuz/measurements_smallscale/smu/'
        ## my meas
        elif data_version=='v2':
            y3rppidir=f'/global/cfs/cdirs/desi/users/siyizhao/Y3/loa-v1/v2/PIP/rppi/'
            y3smudir=f'/global/cfs/cdirs/desi/users/siyizhao/Y3/loa-v1/v2/PIP/smu/'

    ## save clustering data: wp, xi02, cov 
    save_data(tracer, y3rppidir=y3rppidir, y3smudir=y3smudir)
    ## print zmin, zmax, zeff of the z-bins 
    zeff = show_zeff(tracer, data_version=data_version) 
    ## load n(z) of the z-bins
    nz = load_nz(tracer)
    print(nz)
    