# script to read wp and xi0,2 measurements and generate combined jackknife covariance matrix
# from Hanyu Zhang, modified by Siyi Zhao

import argparse
import numpy as np
from pycorr import TwoPointEstimator
import h5py

parser = argparse.ArgumentParser(description='Process LRG data')
parser.add_argument('--input', '-i', default='/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v1.1/PIP/', help='Input directory containing rppi and smu data')
parser.add_argument('--tracer', '-t', default='LRG', help='Tracer type (e.g., LRG, ELG, QSO)')
parser.add_argument('--output', '-o', default='lrg_data_cov.h5', help='Output file path')
args = parser.parse_args()
path2output = args.output
path2input = args.input
y3rppidir = path2input + 'rppi/'
y3smudir = path2input + 'smu/'
tracer = args.tracer

def readwp(path):
    allcounts=TwoPointEstimator.load(path)
    sep, wp, cov = allcounts[::2].get_corr(mode='wp',return_sep=True)
    err=np.sqrt(np.diag(cov))
    return wp, cov, err, allcounts, sep

def readxi02(path):
    allcounts=TwoPointEstimator.load(path)
    sep, xi, cov = allcounts[::2].get_corr(mode='poles',return_sep=True)
    err=np.sqrt(np.diag(cov))
    return xi, cov, err, allcounts, sep

def get_realizations(allcounts,idx,mode):
    jk=np.empty((len(idx),len(allcounts.realizations)))
    for i in allcounts.realizations:
        jk[:,i]=allcounts.realization(i)[::2].get_corr(mode=mode,return_sep=True)[1].flatten()[idx]
    return jk

def get_combined_jkcov(allcountswp,allcountsxi,idxwp,idxxi02):
    jkwp=get_realizations(allcountswp,idxwp,'wp')
    jkxi02=get_realizations(allcountsxi,idxxi02,'poles')
    jkall=np.concatenate((jkwp,jkxi02))
    return (127 * np.cov(jkall,ddof=0)) ##127 is hardcoded, as jackknife have 128 subregions, if you are using a different number please change to Nsub-1

if tracer=='LRG':
    redshift_ranges = {'z0': '0.4-0.6', 'z1': '0.6-0.8', 'z2': '0.8-1.1'}
if tracer=='QSO':
    redshift_ranges = {'z0': '0.8-2.1', 'z1': '0.8-1.1', 'z2': '1.1-1.4', 'z3': '1.4-1.7', 'z4': '1.7-2.1'} #arocher's measure

idxwp=np.arange(3,21) ##scale cut
idxsepxi02=np.arange(8,21)
idxxi02=np.concatenate((np.arange(8,21),np.arange(8+24,21+24)))


wp={}
xi={}
cov={}
data_vector={}
for z in redshift_ranges.keys():
    zmin = redshift_ranges[z].split('-')[0]
    zmax = redshift_ranges[z].split('-')[1]
    wp[z]=readwp(y3rppidir+f'allcounts_{tracer}_GCcomb_{zmin}_{zmax}_pip_angular_bitwise_log_njack128_nran4_split20.npy')
    xi[z]=readxi02(y3smudir+f'allcounts_{tracer}_GCcomb_{zmin}_{zmax}_pip_angular_bitwise_log_njack128_nran4_split20.npy')
    cov[z]=get_combined_jkcov(wp[z][3],xi[z][3],idxwp,idxxi02)
    data_vector[z] = np.concatenate((wp[z][0][idxwp], xi[z][0].flatten()[idxxi02]))

## save to hdf5 file
with h5py.File(path2output, 'w') as f:
    for z in redshift_ranges.keys():
        z_group = f.create_group(z)
        z_group.create_dataset('data_vector', data=data_vector[z])
        z_group.create_dataset('cov', data=cov[z])
        z_group.create_dataset('rp', data=wp[z][4][idxwp])
        z_group.create_dataset('s', data=xi[z][4][idxsepxi02])
        z_group.attrs['redshift_range'] = redshift_ranges[z]
    
    f.attrs['description'] = f'{tracer} clustering measurements: wp + xi0,2'
    f.attrs['original_data_paths'] = f'{y3rppidir}, {y3smudir}'
    f.attrs['jackknife_regions'] = 128
    f.attrs['data_split'] = 'wp: 0-18, xi0: 18-31, xi2: 31-44'
