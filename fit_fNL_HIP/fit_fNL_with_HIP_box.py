"""
HIP.fit_fNL_with_HIPp_box: run desilike analysis to fit fNL using HIP of p for a box mock.
Author: Siyi Zhao
"""

import yaml, os, sys
from desilike.observables.galaxy_clustering import TracerPowerSpectrumMultipolesObservable
from desilike.likelihoods import ObservablesGaussianLikelihood

from desilike.profilers import MinuitProfiler
from desilike.samplers import ZeusSampler
from desilike.samples import plotting

from pathlib import Path
THIS_REPO = Path(__file__).parent.parent
src_path = os.path.abspath(os.path.join(THIS_REPO, 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
from desilike_helper import load_data, plot_observable, prepare_theory
from io_def import ensure_dir

from desilike import setup_logging
setup_logging()


## load config -----------------------------------------------------------------
config_file = sys.argv[1] 
config = yaml.safe_load(open(config_file))
odir = config.get('odir', 'output')
mode = config.get('mode', 'b-p')  # parameterization mode for PNG bias
klim0 = config.get('klim0', [0.003, 0.1])  # k range for monopole fitting

### also enable fixing p, default to False
fix_p = config.get('fix_p', False)
p_fixed_value = config.get('p_fixed_value', 1.0)

## define output ---------------------------------------------------------------
ensure_dir(odir)
fn_triangle = odir+'/triangle.png'
fn_ps = odir+'/power_spectrum.png'
chain_fn = odir + '/chain_zeus'

## define input ----------------------------------------------------------------
z = config['redshift']  # redshift of the catalog
cosmology = 'DESI'
ells = [0]
# ells = (0, 2)

data, cov = load_data(config)

## PNG likelihood
print('Setting up likelihood ...')
priors = config.get('prior', {})
theory = prepare_theory(z=z, mode=mode, priors=priors, fix_fNL=False, fix_p=fix_p, p=p_fixed_value)

## status of all parameters
for key in theory.params:
    print(key, theory.params[key].value, theory.params[key].fixed, theory.params[key].derived, theory.params[key].prior, theory.params[key].ref)

observable = TracerPowerSpectrumMultipolesObservable(data=data, covariance=cov, ells=ells, klim={0: klim0}, theory=theory)

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
chain.write_getdist(chain_fn)
print(chain.to_stats(tablefmt='pretty'))


## bestfit
bestfit_dict = {}
for key in theory.all_params:
    bestfit_value = profiles.bestfit.choice(input=True)[str(key)].value
    theory.init.params[key].update(value=bestfit_value)
    bestfit_dict[str(key)] = bestfit_value

## plot triangle
plotting.plot_triangle(chain, markers={'fnl_loc': bestfit_dict['fnl_loc'], 'p': bestfit_dict['p'], 'b1': bestfit_dict['b1'], 'sn0': bestfit_dict['sn0'], 'sigmas': bestfit_dict['sigmas']}, fn=fn_triangle)

## plot power spectrum
prediction = theory(fnl_loc=bestfit_dict['fnl_loc'], p=bestfit_dict['p'], b1=bestfit_dict['b1'], sn0=bestfit_dict['sn0'], sigmas=bestfit_dict['sigmas'])
plot_observable(observable, prediction, scaling='kpk', fn=fn_ps)

