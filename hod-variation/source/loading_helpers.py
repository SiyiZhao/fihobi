# Credit: https://github.com/ahnyu/hod-variation/blob/main/source/loading_helpers.py


import numpy as np
from pycorr import TwoPointEstimator

def readwp(path):
    allcounts=TwoPointEstimator.load(path)
    sep, wp, cov = allcounts[::2].get_corr(mode='wp',return_sep=True)
    err=np.sqrt(np.diag(cov))
    return wp, cov, err, allcounts

def readxi02(path):
    allcounts=TwoPointEstimator.load(path)
#    print(allcounts[::2].get_corr(mode='ells',return_sep=True))
    sep, xi, cov = allcounts[::2].get_corr(mode='poles',return_sep=True)
    err=np.sqrt(np.diag(cov))
    return xi, cov, err, allcounts

def get_realizations(allcounts,idx,mode):
    jk=np.empty((len(idx),len(allcounts.realizations)))
    for i in allcounts.realizations:
        jk[:,i]=allcounts.realization(i)[::2].get_corr(mode=mode,return_sep=True)[1].flatten()[idx]
    return jk

def get_combined_jkcov(allcountswp,allcountsxi,idxwp,idxxi02):
    jkwp=get_realizations(allcountswp,idxwp,'wp')
    jkxi02=get_realizations(allcountsxi,idxxi02,'poles')
    jkall=np.concatenate((jkwp,jkxi02))
    return (127 * np.cov(jkall,ddof=0))

def cov2corr(cov, return_std=False):
    cov = np.asanyarray(cov)
    std_ = np.sqrt(np.diag(cov))
    corr = cov / np.outer(std_, std_)
    if return_std:
        return corr, std_
    else:
        return corr
    
def nz_comb(N,S,idx):
    return (np.sum(N[idx,-2])+np.sum(S[idx,-2]))/(np.sum(N[idx,-1])+np.sum(S[idx,-1]))


def compute_zeff(*catalog_fns, cosmo=None, zrange=None):
    import fitsio
    import numpy as np
    if cosmo is None:
        from cosmoprimo.fiducial import DESI
        cosmo = DESI()

    def read(fn):
        catalog = fitsio.read(fn)
        z = catalog['Z']
        weights = catalog['WEIGHT'] * catalog['WEIGHT_FKP']
        mask = (z >= zrange[0]) & (z < zrange[1])
        return z[mask], weights[mask]

    z1, weights1 = [np.concatenate(tmp) for tmp in zip(*[read(fn) for fn in catalog_fns])]
    zstep = 0.01
    zbins = np.arange(zrange[0], zrange[1] + zstep / 2., zstep)
    dbins = cosmo.comoving_radial_distance(zbins)
    hist1 = np.histogram(z1, weights=weights1, density=False, bins=zbins)[0]
    zhist1 = np.histogram(z1, weights=z1 * weights1, density=False, bins=zbins)[0]
    z = zhist1 / hist1
    z[np.isnan(z)] = 0.
    dv = dbins[1:]**3 - dbins[:-1]**3
    # sum(dv * density^2 * z) / sum(dv * density^2), where density = hist1 / dv
    return np.sum(hist1**2 / dv * z) / np.sum(hist1**2 / dv)