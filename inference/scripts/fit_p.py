import numpy as np
import yaml
from desilike.theories.galaxy_clustering import FixedPowerSpectrumTemplate, PNGTracerPowerSpectrumMultipoles
from desilike.observables.galaxy_clustering import TracerPowerSpectrumMultipolesObservable
from desilike.likelihoods import ObservablesGaussianLikelihood

from desilike.profilers import MinuitProfiler
from desilike.samplers import ZeusSampler
from desilike.samples import plotting

import os, sys
current_dir = os.getcwd()
source_dir = os.path.join(current_dir, "source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from desilike_helpers import load_data, plot_observable

from desilike import setup_logging
setup_logging()


## load config -----------------------------------------------------------------
name = sys.argv[1] 
odir = sys.argv[2]
config_file = f'configs/{name}.yaml'
config = yaml.safe_load(open(config_file))

## define output ---------------------------------------------------------------
fn_triangle = odir+'/triangle.png'
fn_ps = odir+'/power_spectrum.png'
chain_fn = odir + '/chain_zeus'

## define input ----------------------------------------------------------------
z = config['redshift']  # redshift of the catalog
fnl = config['fnl']
cosmology = 'DESI'
ells = [0]
# ells = (0, 2)

data, cov = load_data(config)

## PNG likelihood
print('Setting up likelihood ...')
template = FixedPowerSpectrumTemplate(z=z, fiducial=cosmology)
# fnl_loc is degenerate with PNG bias bphi. Parameterization is controlled by "mode".
# - "b-p": bphi = 2 * 1.686 * (b1 - p), p as a parameter
# - "bphi": bphi as a parameter
# - "bfnl_loc": bfnl_loc = bphi * fnl_loc as a parameter'
# Here we choose b-p parameterization
theory = PNGTracerPowerSpectrumMultipoles(template=template, mode='b-p')
## fixed fNL
theory.init.params['fnl_loc'].update(value=fnl, fixed=True) 
## other parameters may need larger prior ranges
priors = config.get('prior', {})
for key in priors:
    theory.init.params[key].update(fixed=False, prior=priors[key])
## status of all parameters
for key in theory.params:
    print(key, theory.params[key].value, theory.params[key].fixed, theory.params[key].derived, theory.params[key].prior, theory.params[key].ref)
observable = TracerPowerSpectrumMultipolesObservable(data=data, covariance=cov, 
        klim={0: [0.003, 0.1]},
        # klim={0: [0.003, 0.1, 0.005]},
        # klim={0: [0.005, 0.2, 0.005], 2: [0.005, 0.2, 0.005]}, # fit monopole and quadrupole, between 0.005 and 0.2 h/Mpc
        theory=theory)

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
plotting.plot_triangle(chain, markers={'p': bestfit_dict['p'], 'b1': bestfit_dict['b1'], 'sn0': bestfit_dict['sn0'], 'sigmas': bestfit_dict['sigmas']}, fn=fn_triangle)

## plot power spectrum
prediction = theory(fnl_loc=bestfit_dict['fnl_loc'], p=bestfit_dict['p'], b1=bestfit_dict['b1'], sn0=bestfit_dict['sn0'], sigmas=bestfit_dict['sigmas'])
plot_observable(observable, prediction, scaling='kpk', fn=fn_ps)
