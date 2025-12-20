from desilike.observables.galaxy_clustering import TracerPowerSpectrumMultipolesObservable
from desilike.likelihoods import ObservablesGaussianLikelihood
from desilike.profilers import MinuitProfiler
from desilike.samplers import ZeusSampler
from desilike.samples import plotting

# from data_thecov import read_pk
import os, sys
from desilike import setup_logging
setup_logging()

from pathlib import Path
THIS_REPO = Path(__file__).parent.parent
import sys, os
src_path = os.path.abspath(os.path.join(THIS_REPO, 'src'))
sys.path.insert(0, src_path)
from HIPanOBSample import HIPanOBSample
from io_def import ensure_dir, path_to_catalog, path_to_poles
from thecov_helper import read_mock, power_spectrum, thecov_box
from desilike_helper import prepare_theory, plot_observable

WORK_DIR = Path(sys.argv[1])
i = sys.argv[2] 

print(f"Working directory: {WORK_DIR}\n")

hip = HIPanOBSample(cfg_file=WORK_DIR / "config.yaml")

priors = {
    'p': {'limits': (-1., 3.)},
    'sigmas': {'limits': (0., 20.)},
}


fname = path_to_catalog(sim_params=hip.cfgHOD['sim_params'], tracer=hip.OBSample['tracer'], prefix=f'r{i}')
path2poles = path_to_poles(sim_params=hip.cfgHOD['sim_params'], tracer=hip.OBSample['tracer'], prefix=f'r{i}')
ODIR = WORK_DIR / "HIP" / f"mock_{i}"
# ODIR = WORK_DIR / "HIP" / "mocks" / f"r{i}"
ensure_dir(ODIR)
fn_chain = ODIR / "chain_zeus"
fn_ps = ODIR / "power_spectrum.png"
fn_triangle = ODIR / "triangle.png"

mode = 'b-p'
fnl = 100
ells = [0]
klim = {0: [0.003, 0.1]}
## measure power spectrum
boxL = 2000.0  # Mpc/h
boxV = boxL**3  # (Mpc/h)^3
pos, nbar = read_mock(fname, boxV=boxV)
data = power_spectrum(pos, path2poles=path2poles)
cov = thecov_box(pk_theory=data, nbar=nbar, volume=boxV, has_shotnoise_set=False)

theory = prepare_theory(z=hip.OBSample['zsnap'], cosmology='DESI', mode=mode, fnl=fnl, priors=priors, fix_fNL=True)



## status of all parameters
for key in theory.params:
    print(key, theory.params[key].value, theory.params[key].fixed, theory.params[key].derived, theory.params[key].prior, theory.params[key].ref)


observable = TracerPowerSpectrumMultipolesObservable(data=data['P_0'], covariance=cov, ells=ells, k=data['k'], klim=klim, theory=theory)

likelihood = ObservablesGaussianLikelihood(observables=[observable])

likelihood()  # just to initialize


## sampling
print('Minuit Profiler...')
# Seed used to decide on starting point
profiler = MinuitProfiler(likelihood, seed=42)
# Find best fit, starting from 5 different starting points
# NOTE: With MPI, these runs are performed in parallel
profiles = profiler.maximize(niterations=5)
print(profiles.to_stats(tablefmt='pretty'))
print('Zeus Sampler...')
sampler = ZeusSampler(likelihood, seed=42)
sampler.run(check={'max_eigen_gr': 0.04})
chain = sampler.chains[0].remove_burnin(0.5)
chain.write_getdist(fn_chain)
print(chain.to_stats(tablefmt='pretty'))

## bestfit
# best_p = profiles.bestfit.choice(input=True)['p'].value
bestfit_dict = {}
for key in theory.all_params:
    bestfit_value = profiles.bestfit.choice(input=True)[str(key)].value
    theory.init.params[key].update(value=bestfit_value)
    bestfit_dict[str(key)] = bestfit_value

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
