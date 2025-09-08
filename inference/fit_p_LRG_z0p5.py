import numpy as np

from cosmoprimo.fiducial import DESI

from desilike.theories.galaxy_clustering import FixedPowerSpectrumTemplate, PNGTracerPowerSpectrumMultipoles
from desilike.observables.galaxy_clustering import TracerPowerSpectrumMultipolesObservable
from desilike.likelihoods import ObservablesGaussianLikelihood

from desilike.profilers import MinuitProfiler
from desilike.samplers import ZeusSampler
from desilike.samples import plotting

from desilike import setup_logging
setup_logging()


## define output
fn_triangle = 'out/fit_p_LRG_z0p5_triangle.png'
fn_ps = 'out/fit_p_LRG_z0p5_power_spectrum.png'

## define input 
z = 0.5
fnl = 30.
cosmology = 'DESI' 

## data (fake now)
print('Loading data ...')
data = np.load('test_data/Pk_mock_LRG_fNL30_z0p5.npy', allow_pickle=True)
k_abacus = data.item()['k']
data_abacus = data.item()['data']
cov_ezmocks = data.item()['cov']

## PNG likelihood
print('Setting up likelihood ...')
template = FixedPowerSpectrumTemplate(z=z, fiducial=cosmology)
# fnl_loc is degenerate with PNG bias bphi. Parameterization is controlled by "mode".
# - "b-p": bphi = 2 * 1.686 * (b1 - p), p as a parameter
# - "bphi": bphi as a parameter
# - "bfnl_loc": bfnl_loc = bphi * fnl_loc as a parameter'
# Here we choose b-p parameterization
theory = PNGTracerPowerSpectrumMultipoles(template=template, mode='b-p')
theory.init.params['fnl_loc'].update(value=fnl, fixed=True) 
theory.init.params['p'].update(fixed=False, prior={'min': -2., 'max': 4.})
observable = TracerPowerSpectrumMultipolesObservable(data=data_abacus, covariance=cov_ezmocks, ells=(0, 2), k=k_abacus,
        #klim={0: [0.005, 0.2]},
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
print(chain.to_stats(tablefmt='pretty'))

bestfit_dict = {}
for key in theory.all_params:
    bestfit_value = profiles.bestfit.choice(input=True)[str(key)].value
    theory.init.params[key].update(value=bestfit_value)
    bestfit_dict[str(key)] = bestfit_value

## plot
plotting.plot_triangle(chain, markers={'p': bestfit_dict['p'], 'b1': bestfit_dict['b1'], 'sn0': bestfit_dict['sn0'], 'sigmas': bestfit_dict['sigmas']}, fn=fn_triangle)


from matplotlib import pyplot as plt

def plot_observable(observable, theory, scaling='kpk',fn=None):
    'Plot the observable compared to the best-fit theory prediction. Code adapted from desilike.observables.galaxy_clustering.TracerPowerSpectrumMultipolesObservable.plot()'
    ells = observable.ells
    kw_theory = {}
    if isinstance(kw_theory, dict):
        kw_theory = [kw_theory]
    if len(kw_theory) != len(ells):
        kw_theory = [{key: value for key, value in kw_theory[0].items() if (key != 'label') or (ill == 0)} for ill in range(len(ells))]

    kw_theory = [{'color': 'C{:d}'.format(ill), **kw} for ill, kw in enumerate(kw_theory)]

    
    height_ratios = [max(len(ells), 3)] + [1] * len(ells)
    figsize = (6, 1.5 * sum(height_ratios))
    fig, lax = plt.subplots(len(height_ratios), sharex=True, sharey=False, gridspec_kw={'height_ratios': height_ratios}, figsize=figsize, squeeze=True)
    fig.subplots_adjust(hspace=0.1)
    show_legend = True

    k = observable.k
    data, std = observable.data, observable.std
    k_exp = 1 if scaling == 'kpk' else 0

    for ill, ell in enumerate(ells):
        lax[0].errorbar(k[ill], k[ill]**k_exp * data[ill], yerr=k[ill]**k_exp * std[ill], color='C{:d}'.format(ill), alpha=0.7, barsabove=True, linestyle='none', marker='o', label=r'$\ell = {:d}$'.format(ell))
        lax[0].plot(k[ill], k[ill]**k_exp * theory[ill], **kw_theory[ill])
    for ill, ell in enumerate(ells):
        lax[ill + 1].plot(k[ill], (data[ill] - theory[ill]) / std[ill], **kw_theory[ill])
        lax[ill + 1].set_ylim(-4, 4)
        for offset in [-2., 2.]: lax[ill + 1].axhline(offset, color='k', linestyle='--')
        lax[ill + 1].set_ylabel(r'$\Delta P_{{{0:d}}} / \sigma_{{ P_{{{0:d}}} }}$'.format(ell))
    for ax in lax: ax.grid(True)
    if show_legend: lax[0].legend()
    if scaling == 'kpk':
        lax[0].set_ylabel(r'$k P_{\ell}(k)$ [$(\mathrm{Mpc}/h)^{2}$]')
    if scaling == 'loglog':
        lax[0].set_ylabel(r'$P_{\ell}(k)$ [$(\mathrm{Mpc}/h)^{3}$]')
        lax[0].set_yscale('log')
        lax[0].set_xscale('log')
    lax[-1].set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
    if fn is not None:
        fig.savefig(fn, bbox_inches='tight')
        print(f'Saved power spectrum plot to {fn}')
    else:
        plt.show()


prediction = theory(fnl_loc=bestfit_dict['fnl_loc'], p=bestfit_dict['p'], b1=bestfit_dict['b1'], sn0=bestfit_dict['sn0'], sigmas=bestfit_dict['sigmas'])
plot_observable(observable, prediction, scaling='kpk', fn=fn_ps)
