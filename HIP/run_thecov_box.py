#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_thecov_box.py
-----------------
Compute Gaussian and trispectrum (T0) covariance matrices using thecov package.

Usage:
    python run_thecov_box.py
    
Dependencies:
    - thecov: installed in ~/lib/
    - powercovfft: installed by `pip install powercovfft@git+https://github.com/archaeo-pteryx/PowerSpecCovFFT.git`
    - cosmoprimo: installed @NERSC and load by `source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main`

Author: Mengfan He & Siyi Zhao
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.expanduser('~/lib/thecov'))
from thecov import geometry, covariance
import cosmoprimo

def read_bias(path2dir):
    """
    Read bias value from mock_bias.txt file for given HOD model and redshift.
    """
    bias_file = path2dir + 'mock_bias.txt'
    try:
        bias = np.loadtxt(bias_file)
        print(f"Read bias {bias} from {bias_file}")
        return bias
    except Exception as e:
        print(f"Error reading bias from {bias_file}: {e}")
        return None

def detect_nbar(path2dir, volume=2000**3):
    """
    Detect number density nbar from the mock catalog for given HOD model and redshift.
    """
    fname = path2dir + 'QSOs.dat'  
    try:
        print(f"Loading mock from {fname}")
        with open(fname, 'r') as f:
            it = iter(f)
            for line in it:
                if not line.lstrip().startswith('#'):
                    break
            data = np.loadtxt(it)
        n_galaxies = data.shape[0]
        nbar = n_galaxies / volume
        print(f"Detected nbar {nbar} from {fname}")
        return nbar
    except Exception as e:
        print(f"Error detecting nbar from {fname}: {e}")
        return None

def read_pk(path2dir):
    """
    Read mock power spectrum to a dictionary for given HOD model and redshift.
    """
    pk_file = path2dir + 'pypower2powspec.txt'
    try:
        data = np.loadtxt(pk_file)
        kmin, kmax = data[:, 1], data[:, 2]
        p0 = data[:, 5]
        p2 = data[:, 6]
        # build mask to remove NaNs and other non-finite values
        mask = np.isfinite(kmin) & np.isfinite(kmax) & np.isfinite(p0) & np.isfinite(p2)
        if not np.any(mask):
            raise ValueError(f"No valid k-bins or power values found in {pk_file}")
        pk_theory = {
            'kmin': kmin[mask],
            'kmax': kmax[mask],
            'P_0': p0[mask],
            'P_2': p2[mask],
        }
        print(f"Read theoretical power spectrum from {pk_file}")
        return pk_theory
    except Exception as e:
        print(f"Error reading power spectrum from {pk_file}: {e}")
        return None


def cal_thecov_box(pk_theory, zeff, b1, nbar, cosmo, volume=2000**3,
                   nthreads=24, has_shotnoise_set=False, resume_file=None,
                   save_prefix='covariance_output'):
    """
    Compute Gaussian and trispectrum (T0) covariance matrices and save to disk.
    """

    # Create geometry
    geom = geometry.BoxGeometry(volume=volume, nbar=nbar)

    # Define k-bins
    kmin, kmax, dk = pk_theory['kmin'][0], pk_theory['kmax'][-1], pk_theory['kmax'][0] - pk_theory['kmin'][0]
    print(f"Number of bins: {(kmax - kmin) / dk:.0f}")

    # ========== Gaussian Covariance ==========
    gaussian = covariance.GaussianCovariance(geom)
    gaussian.set_kbins(kmin, kmax, dk)
    gaussian.set_galaxy_pk_multipole(pk_theory['P_0'], 0, has_shotnoise=has_shotnoise_set)
    gaussian.set_galaxy_pk_multipole(pk_theory['P_2'], 2)
    # gaussian.set_galaxy_pk_multipole(pk_theory['P_4'], 4)
    gaussian.compute_covariance()

    # ========== Trispectrum (T0) Covariance ==========
    t0 = covariance.RegularTrispectrumCovariance(geom)
    t0.set_kbins(kmin, kmax, dk)

    plin = cosmo.get_fourier()
    t0.set_linear_matter_pk(np.vectorize(lambda k: plin.pk_kz(k, zeff)))
    t0.set_params(fgrowth=cosmo.growth_rate(zeff), b1=b1)
    t0.compute_covariance()

    # ========== Save both to disk ==========
    os.makedirs(os.path.dirname(save_prefix), exist_ok=True)
    combine = gaussian+t0
    out_dict = {
        'gaussian_cov_P0': gaussian.get_ell_cov(0, 0).cov,
        'gaussian_cov_P2': gaussian.get_ell_cov(2, 2).cov,
        't0_cov_P0': t0.get_ell_cov(0, 0).cov,
        't0_cov_P2': t0.get_ell_cov(2, 2).cov,
        'comb_cov_P0': combine.get_ell_cov(0, 0).cov,
        'comb_cov_P2': combine.get_ell_cov(2, 2).cov,
        'k_min': kmin,
        'k_max': kmax,
        'dk': dk,
        'zeff': zeff,
        'b1': b1,
        'volume': volume,
        'nbar': nbar,
    }

    np.save(f"{save_prefix}_gaussian_t0.npy", out_dict)
    print(f"Saved Gaussian and T0 covariance to {save_prefix}_gaussian_t0.npy")

    return gaussian, t0


if __name__ == "__main__":
    # Define fiducial cosmology used in calculations
    cosmo = cosmoprimo.fiducial.DESI()

    # Settings
    hod_model = ''
    # hod_model = '_base-A-dv'
    zeff = 3.0
    # zeff = 0.95 # effective redshift
    path2dir=f'/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks{hod_model}/Abacus_pngbase_c302_ph000/z{zeff:.3f}/galaxies_rsd_dv/'
    bias = read_bias(path2dir) # linear bias
    nbar = detect_nbar(path2dir) # number density in (Mpc/h)^-3
    pk_theory = read_pk(path2dir)
    OFILE_PREFIX = path2dir + f'thecov_output_b1_{bias}_sn'

    gaussian, t0 = cal_thecov_box(pk_theory, zeff, bias, nbar, cosmo, save_prefix=OFILE_PREFIX)
    