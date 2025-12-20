import numpy as np
import cosmoprimo

from io_def import read_catalog
from pypower_helpers import run_pypower_redshift
from mock_bias import load_Abacus_linear_power, grow_plin, measure_bias_k, average_bias

import sys, os
sys.path.insert(0, os.path.expanduser('~/lib/thecov'))
from thecov import geometry, covariance

def read_mock(fname: str, boxV: float) -> tuple[np.ndarray, float]:
    pos = read_catalog(fname)  
    n_galaxies = pos.shape[0]
    nbar = n_galaxies / boxV
    return pos, nbar

def power_spectrum(pos: np.ndarray, path2poles: str | None = None) -> dict:
    poles = run_pypower_redshift(pos[:,0], pos[:,1], pos[:,2])
    if path2poles is not None:
        poles.save(path2poles)
    kbin = poles.edges[0]
    kmins, kmaxs = kbin[:-1], kbin[1:]
    k, p0 = poles(ell=0, return_k=True, complex=False)
    p2 = poles(ell=2, return_k=False, complex=False)
    # build mask to remove NaNs and other non-finite values
    mask = np.isfinite(kmins) & np.isfinite(kmaxs) & np.isfinite(p0) & np.isfinite(p2) & (k < 0.1) & (k>0.003)
    kmins, kmaxs = kmins[mask], kmaxs[mask]
    data = {
        'kmin': kmins[0],
        'kmax': kmaxs[-1],
        'dk': kmaxs[0] - kmins[0],
        'k': k[mask],
        'P_0': p0[mask],
        'P_2': p2[mask],
    }
    return data

def linear_matter_power_spectrum(zeff: float, IDIR: str = "/global/homes/s/siyizhao/lib/AbacusSummit/Cosmologies/abacus_cosm000/") -> tuple[np.ndarray, np.ndarray]:
    klin, plin_z1 = load_Abacus_linear_power(IDIR)
    plin_z = grow_plin(zeff, plin_z1, IDIR=IDIR, z_in=1.0)
    return klin, plin_z

def linear_bias(data: dict, klin: np.ndarray, plin_z: np.ndarray, bkmin: float = 0.05, bkmax: float = 0.10,) -> float:
    k_mock = data['k']
    P0_mock = data['P_0']
    k_plot, bk = measure_bias_k(k_mock, P0_mock, klin, plin_z)
    bias = average_bias(k_plot, bk, bkmin=bkmin, bkmax=bkmax)
    return bias

def thecov_box(
    pk_theory: dict, 
    nbar: float, 
    volume: float = 2000**3, 
    has_shotnoise_set: bool = False,
    want_T0: bool = False,
    zeff: float | None = None,
    b1: float | None = None,
    cosmo: cosmoprimo.Cosmology | None = None,
) -> np.ndarray:
    """
    pk_theory: dict with keys 'kmin', 'kmax', 'dk', 'P_0', 'P_2',
    zeff, b1, cosmo: required if want_T0 is True
    """
    # Create geometry
    geom = geometry.BoxGeometry(volume=volume, nbar=nbar)
    # Define k-bins
    # kmin, kmax, dk = pk_theory['kmin'][0], pk_theory['kmax'][-1], pk_theory['kmax'][0] - pk_theory['kmin'][0]
    kmin, kmax, dk = pk_theory['kmin'], pk_theory['kmax'], pk_theory['dk']
    # ========== Gaussian Covariance ==========
    gaussian = covariance.GaussianCovariance(geom)
    gaussian.set_kbins(kmin, kmax, dk)
    gaussian.set_galaxy_pk_multipole(pk_theory['P_0'], 0, has_shotnoise=has_shotnoise_set)
    gaussian.set_galaxy_pk_multipole(pk_theory['P_2'], 2)
    # gaussian.set_galaxy_pk_multipole(pk_theory['P_4'], 4)
    gaussian.compute_covariance()
    
    # # ========== Trispectrum (T0) Covariance ==========
    # t0 = covariance.RegularTrispectrumCovariance(geom)
    # t0.set_kbins(kmin, kmax, dk)

    # plin = cosmo.get_fourier()
    # t0.set_linear_matter_pk(np.vectorize(lambda k: plin.pk_kz(k, zeff)))
    # t0.set_params(fgrowth=cosmo.growth_rate(zeff), b1=b1)
    # t0.compute_covariance()
    
    # ========== Combine Gaussian and T0 Covariance ==========
    combine = gaussian#+t0
    comb_cov_P0 = combine.get_ell_cov(0, 0).cov
    return comb_cov_P0
