"""
src.HOD_prepare

Refer to: https://github.com/ahnyu/hod-variation/blob/main/source/loading_helpers.py
"""

import numpy as np
from pycorr import TwoPointEstimator

__all__ = [
    "save_data_for_HODfitting",
    "show_zeff",
    "load_nz"
    ]

# ======== small scale clusterings ========

def readwp(path):
    allcounts=TwoPointEstimator.load(path)
    sep, wp, cov = allcounts[::2].get_corr(mode='wp',return_sep=True)
    err=np.sqrt(np.diag(cov))
    return wp, cov, err, allcounts

def readxi02(path):
    allcounts=TwoPointEstimator.load(path)
    # print(allcounts[::2].get_corr(mode='ells',return_sep=True))
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


def save_data_for_HODfitting(
    outdir, 
    y3rppidir, 
    y3smudir, 
    tracer, 
    zmin, 
    zmax,
    idx_min_rp=6,
    idx_max_rp=21,
    idx_min_s=11,
    idx_max_s=21,
    ):
    """
    Refer to: https://github.com/ahnyu/hod-variation/blob/main/prep_data_v1.1.ipynb
    """
    ## rp/s bin midpoints saved to data files
    rpbins=np.geomspace(0.01,100,25)
    print('x bins:', rpbins)
    rpbinsmid=(rpbins[1:]+rpbins[:-1])/2
    ## read data
    fname = f"allcounts_{tracer}_GCcomb_{zmin:.1f}_{zmax:.1f}_pip_angular_bitwise_log_njack128_nran4_split20.npy"
    wp = readwp(y3rppidir / fname)
    xi = readxi02(y3smudir / fname)
    ## get jackknife covariance
    idx_wp_cut   = np.arange(idx_min_rp, idx_max_rp)  
    idx_xi_cut  = np.arange(idx_min_s, idx_max_s)
    idx_xi02_cut = np.concatenate((idx_xi_cut, idx_xi_cut + 24))  
    cov = get_combined_jkcov(wp[3], xi[3], idx_wp_cut, idx_xi02_cut)
    ## save cut data
    path2data = {
        "path2cov": str(outdir/f"cov_{tracer}_{zmin:.1f}_{zmax:.1f}_cut.dat"),
        "path2wp": str(outdir/f"wp_{tracer}_{zmin:.1f}_{zmax:.1f}_cut.dat"),
        "path2xi02": str(outdir/f"xi02_{tracer}_{zmin:.1f}_{zmax:.1f}_cut.dat")
    }
    ## save wp cut
    np.savetxt(path2data["path2wp"],
                np.column_stack((rpbinsmid[idx_wp_cut],
                                    wp[0][idx_wp_cut],
                                    wp[2][idx_wp_cut])))
    ## save xi02 cut
    np.savetxt(path2data["path2xi02"],
                np.column_stack((rpbinsmid[idx_xi_cut],
                                    xi[0][0][idx_xi_cut],       
                                    xi[2][idx_xi_cut],          
                                    xi[0][1][idx_xi_cut],       
                                    xi[2][idx_xi_cut + 24])))   
    ## save cov cut
    np.savetxt(path2data["path2cov"], cov)
    print(f"[write] -> {outdir}")
    return path2data

# ======== effective redshift of the catalog ========

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

def show_zeff(tracer, zmin, zmax, catdir):
    ''' measure zeff for a given tracer 
    tracer: 'LRG', 'QSO', 'highz-QSO'
    '''
    zeff_NGC = compute_zeff(catdir/f'{tracer}_NGC_clustering.dat.fits',zrange=[zmin, zmax])
    zeff_SGC = compute_zeff(catdir/f'{tracer}_SGC_clustering.dat.fits',zrange=[zmin, zmax])
    zeff_data = {'NGC': float(zeff_NGC), 'SGC': float(zeff_SGC)}
    print(tracer, zmin,'-', zmax, 'zeff of NGC:', zeff_NGC, ', zeff of SGC:', zeff_SGC)
    return zeff_data

# ======== number density ========

def nz_comb(N,S,idx):
    return (np.sum(N[idx,-2])+np.sum(S[idx,-2]))/(np.sum(N[idx,-1])+np.sum(S[idx,-1]))

def load_nz(tracer, zmin, zmax, nzdir):
    ''' load n(z) for a given tracer 
    tracer: 'LRG', 'QSO', 'highz-QSO'
    '''
    ## Read n(z) for NGC and SGC
    nz_NGC=np.loadtxt(nzdir/f'{tracer}_NGC_nz.txt',skiprows=2)
    nz_SGC=np.loadtxt(nzdir/f'{tracer}_SGC_nz.txt',skiprows=2)
    ## combine NGC and SGC
    z_idx=np.where((nz_NGC[:,0]>=zmin) & (nz_NGC[:,0]<zmax))[0]
    nz_data=nz_comb(nz_NGC,nz_SGC,z_idx)
    return float(nz_data)
