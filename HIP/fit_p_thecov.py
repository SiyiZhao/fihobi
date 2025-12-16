import numpy as np
import yaml

from desilike.samplers import ZeusSampler
from desilike.samples import plotting

# from data_thecov import read_pk
import os, sys
current_dir = os.getcwd()
source_dir = os.path.join("../inference/source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from desilike_helpers import load_data, plot_observable

from desilike import setup_logging
setup_logging()


import cosmoprimo
from pypower import PowerSpectrumMultipoles
from pathlib import Path
import numpy as np
from run_thecov_box import cal_thecov_box
import sys, os
sys.path.insert(0, os.path.expanduser('../src'))
from io_def import read_catalog
from pypower_helpers import run_pypower_redshift
from mock_bias import load_Abacus_linear_power, grow_plin, measure_bias_k, average_bias, plot_bias
from desilike_helper import prepare_theory_fix_fNL, bestfit_p_inference

# kmax = 0.10053096491487339
# # kedges = np.linspace(0, kmax, 32)
# kedges = np.linspace(0, kmax, 18)
# edges = (kedges, np.linspace(-1., 1., 5))
name = sys.argv[1] 
odir = sys.argv[2]
prefix = sys.argv[3]

zeff = 3.0
fname = f'/global/homes/s/siyizhao/projects/fihobi/hod-variation/output/desi-dr2-hod/mocks_base_v2/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z3p000/abacus_HF_QSO_3p000_DR2_v2.0_Abacus_pngbase_c302_ph000_{prefix}_clustering.dat.h5'
# fname = f'/global/homes/s/siyizhao/projects/fihobi/hod-variation/output/desi-dr2-hod/mocks_base-A_v2/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z3p000/abacus_HF_QSO_3p000_DR2_v2.0_Abacus_pngbase_c302_ph000_{prefix}_clustering.dat.h5'
path2dir = Path(fname).parent.as_posix() + '/'
path2poles = path2dir + f'{prefix}_pypower_poles.npy'
OFILE_PREFIX = path2dir + f'{prefix}_thecov_sn'


## measure power spectrum
pos = read_catalog(fname)  
n_galaxies = pos.shape[0]
volume = 2000**3  # (Mpc/h)^3
nbar = n_galaxies / volume
print(f"Number of galaxies: {n_galaxies}, Volume: {volume}, nbar: {nbar:.3e} (Mpc/h)^-3")

def read_pk(fname: str)-> dict:
    """Read power spectrum multipoles from pypower output file.

    Args:
        fname (str): Path to the pypower output .npy file.
    Returns:
        dict: Dictionary containing k values and power spectrum multipoles.
    """
    poles = PowerSpectrumMultipoles.load(fname)
    kbin = poles.edges[0]
    kmin, kmax = kbin[:-1], kbin[1:]
    k, p0 = poles(ell=0, return_k=True, complex=False)
    p2 = poles(ell=2, return_k=False, complex=False)
    # build mask to remove NaNs and other non-finite values
    mask = np.isfinite(kmin) & np.isfinite(kmax) & np.isfinite(p0) & np.isfinite(p2) & (k < 0.1) & (k>0.003)
    if not np.any(mask):
        raise ValueError(f"No valid k-bins or power values found in {fname}")

    pk_theory = {
            'kmin': kmin[mask],
            'kmax': kmax[mask],
            'k': k[mask],
            'P_0': p0[mask],
            'P_2': p2[mask],
        }
    print(f"Read theoretical power spectrum from {fname}")
    return pk_theory

poles = run_pypower_redshift(pos[:,0], pos[:,1], pos[:,2])
# poles = run_pypower_redshift(pos[:,0], pos[:,1], pos[:,2],edges=edges)
poles.save(path2poles)
print(f"Saved power spectrum multipoles to {path2poles}")
pk_theory = read_pk(path2poles)
k_mock = pk_theory['k']
P0_mock = pk_theory['P_0']

## measure bias 

bkmin = 0.05
bkmax = 0.10
IDIR = "/global/homes/s/siyizhao/lib/AbacusSummit/Cosmologies/abacus_cosm000/"
fn_out = odir+'/mock_bias.png'
klin, plin_z1 = load_Abacus_linear_power(IDIR)
plin_z = grow_plin(zeff, plin_z1, IDIR=IDIR, z_in=1.0)
k_plot, bk = measure_bias_k(k_mock, P0_mock, klin, plin_z)
bias = average_bias(k_plot, bk, bkmin=bkmin, bkmax=bkmax)
# bias = 4.025
plot_bias(k_plot, bk, bias, bkmin, bkmax, fn=fn_out)

## thecov
cosmo = cosmoprimo.fiducial.DESI()
gaussian, t0 = cal_thecov_box(pk_theory, zeff, bias, nbar, cosmo, save_prefix=OFILE_PREFIX)



## load config -----------------------------------------------------------------
# config_file = f'../inference/configs/{name}.yaml'
config_file = f'../inference/configs/QSO-z6_fNL100_base-A-dv.yaml'
config = yaml.safe_load(open(config_file))
mode = 'b-p'
klim0 = [0.003, 0.1]
## define output ---------------------------------------------------------------
fn_triangle = odir+'/triangle.png'
fn_ps = odir+'/power_spectrum.png'
chain_fn = odir + '/chain_zeus'

## define input ----------------------------------------------------------------
z = 3
fnl = 100
cosmology = 'DESI'
ells = [0]

def read_cov(fname: str) -> np.ndarray:
    data = np.load(fname, allow_pickle=True).item()
    comb_cov_P0 = data['comb_cov_P0']
    return comb_cov_P0

data = read_pk(path2poles)
print('Data k:', data['k'])
print('Data P0:', data['P_0'])
cov = read_cov(path2dir + f'{prefix}_thecov_sn_gaussian_t0.npy')


## PNG likelihood
print('Setting up likelihood ...')
priors = config.get('prior', {})
theory = prepare_theory_fix_fNL(z=z, mode=mode, fnl=fnl, priors=priors)
## status of all parameters
for key in theory.params:
    print(key, theory.params[key].value, theory.params[key].fixed, theory.params[key].derived, theory.params[key].prior, theory.params[key].ref)

bestfit_dict, likelihood, observable = bestfit_p_inference(theory=theory, data=data['P_0'], cov=cov, ells=ells, k=data['k'], klim={0: klim0})

## sampling
print('Zeus Sampler...')
sampler = ZeusSampler(likelihood, seed=42)
sampler.run(check={'max_eigen_gr': 0.04})
chain = sampler.chains[0].remove_burnin(0.5)
chain.write_getdist(chain_fn)
print(chain.to_stats(tablefmt='pretty'))


## plot triangle
if mode == 'b-p':
    plotting.plot_triangle(chain, markers={'p': bestfit_dict['p'], 'b1': bestfit_dict['b1'], 'sn0': bestfit_dict['sn0'], 'sigmas': bestfit_dict['sigmas']}, fn=fn_triangle)
elif mode == 'bphi':
    plotting.plot_triangle(chain, markers={'bphi': bestfit_dict['bphi'], 'b1': bestfit_dict['b1'], 'sn0': bestfit_dict['sn0'], 'sigmas': bestfit_dict['sigmas']}, fn=fn_triangle)
else:
    raise NotImplementedError(f"Mode {mode} not implemented for triangle plot.")

## plot power spectrum
if mode == 'b-p':
    prediction = theory(fnl_loc=bestfit_dict['fnl_loc'], p=bestfit_dict['p'], b1=bestfit_dict['b1'], sn0=bestfit_dict['sn0'], sigmas=bestfit_dict['sigmas'])
elif mode == 'bphi':
    prediction = theory(fnl_loc=bestfit_dict['fnl_loc'], bphi=bestfit_dict['bphi'], b1=bestfit_dict['b1'], sn0=bestfit_dict['sn0'], sigmas=bestfit_dict['sigmas'])
else:
    raise NotImplementedError(f"Mode {mode} not implemented for power spectrum plot.")
plot_observable(observable, prediction, scaling='kpk', fn=fn_ps)
