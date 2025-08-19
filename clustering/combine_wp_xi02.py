# script to read wp and xi0,2 measurements and generate combined jackknife covariance matrix
# from Hanyu Zhang, modified by Siyi Zhao

import argparse
import numpy as np
from pycorr import TwoPointEstimator
import h5py

parser = argparse.ArgumentParser(description='Process LRG data')
parser.add_argument('--output', '-o', default='lrg_data_cov.h5', help='Output file path')
args = parser.parse_args()
path2output = args.output

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

y3rppidir='/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v1.1/PIP/rppi/'
y3smudir='/global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v1.1/PIP/smu/'

idxwp=np.arange(3,21) ##scale cut
idxsepxi02=np.arange(8,21)
idxxi02=np.concatenate((np.arange(8,21),np.arange(8+24,21+24)))

wplrg={}
wplrg['z0']=readwp(y3rppidir+'allcounts_LRG_GCcomb_0.4_0.6_pip_angular_bitwise_log_njack128_nran4_split20.npy')
wplrg['z1']=readwp(y3rppidir+'allcounts_LRG_GCcomb_0.6_0.8_pip_angular_bitwise_log_njack128_nran4_split20.npy')
wplrg['z2']=readwp(y3rppidir+'allcounts_LRG_GCcomb_0.8_1.1_pip_angular_bitwise_log_njack128_nran4_split20.npy')
xilrg={}
xilrg['z0']=readxi02(y3smudir+'allcounts_LRG_GCcomb_0.4_0.6_pip_angular_bitwise_log_njack128_nran4_split20.npy')
xilrg['z1']=readxi02(y3smudir+'allcounts_LRG_GCcomb_0.6_0.8_pip_angular_bitwise_log_njack128_nran4_split20.npy')
xilrg['z2']=readxi02(y3smudir+'allcounts_LRG_GCcomb_0.8_1.1_pip_angular_bitwise_log_njack128_nran4_split20.npy')
covlrg={}
covlrg['z0']=get_combined_jkcov(wplrg['z0'][3],xilrg['z0'][3],idxwp,idxxi02)
covlrg['z1']=get_combined_jkcov(wplrg['z1'][3],xilrg['z1'][3],idxwp,idxxi02)
covlrg['z2']=get_combined_jkcov(wplrg['z2'][3],xilrg['z2'][3],idxwp,idxxi02)

# following add by Siyi Zhao
data_vector={}
data_vector['z0'] = np.concatenate((wplrg['z0'][0][idxwp], xilrg['z0'][0].flatten()[idxxi02]))
data_vector['z1'] = np.concatenate((wplrg['z1'][0][idxwp], xilrg['z1'][0].flatten()[idxxi02]))
data_vector['z2'] = np.concatenate((wplrg['z2'][0][idxwp], xilrg['z2'][0].flatten()[idxxi02]))

## save to hdf5 file
with h5py.File(path2output, 'w') as f:
    redshift_ranges = {'z0': '0.4-0.6', 'z1': '0.6-0.8', 'z2': '0.8-1.1'}
    
    for z in ['z0', 'z1', 'z2']:
        z_group = f.create_group(z)
        z_group.create_dataset('data_vector', data=data_vector[z])
        z_group.create_dataset('cov', data=covlrg[z])
        z_group.create_dataset('rp', data=wplrg[z][4][idxwp])
        z_group.create_dataset('s', data=xilrg[z][4][idxsepxi02])
        
        z_group.attrs['redshift_range'] = redshift_ranges[z]
    
    f.attrs['description'] = f'LRG clustering measurements: wp + xi0,2'
    f.attrs['original_data_paths'] = f'{y3rppidir}, {y3smudir}'
    f.attrs['jackknife_regions'] = 128
    f.attrs['data_split'] = 'wp: 0-18, xi0: 18-31, xi2: 31-44'
