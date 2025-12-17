import numpy as np
import os
from pypower import PowerSpectrumMultipoles
from matplotlib import pyplot as plt

from desilike.theories.galaxy_clustering import FixedPowerSpectrumTemplate, PNGTracerPowerSpectrumMultipoles
from desilike.observables.galaxy_clustering import TracerPowerSpectrumMultipolesObservable
from desilike.likelihoods import ObservablesGaussianLikelihood
from desilike.profilers import MinuitProfiler


def load_data(config):
    '''
    Prepare data and covariance for desilike.
    
    Parameters
    ----------
    config : dict
        Configuration dictionary containing input paths.
        
    Returns
    -------
    data : pypower.PowerSpectrumMultipoles
        The power spectrum multipoles of the Abacus mock.
    cov : list of pypower.PowerSpectrumMultipoles or paths to such files
        Covariance matrix estimated from EZmocks.
    '''
    n_EZmocks = config.get('n_EZmocks', None)
    config_input = config['input']
    abacus_poles = config_input['abacus_poles']  # path to the power spectrum multipoles from AbacusHOD mock
    ezmock_poles = config_input['ezmock_poles']  # path to the power spectrum multipoles from EZmocks, used to estimate covariance matrix

    ## load data
    print('Loading data ...')
    data = PowerSpectrumMultipoles.load(abacus_poles)
    ezmock_p = str(ezmock_poles)
    if os.path.isdir(ezmock_p):
        # load all .npy mock pypower.PowerSpectrumMultipoles files in the directory, the list of the file names will be passed to desilike to estimate covariance
        cov = sorted([os.path.join(ezmock_p, f) for f in os.listdir(ezmock_p) if f.lower().endswith(('.npy'))])
        if len(cov) == 0:
            raise FileNotFoundError(f'No .npy files found in directory {ezmock_p}')
    else:
        print(f'Read covariance from a single file {ezmock_poles} ...')
        cov = np.load(ezmock_poles, allow_pickle=True)
        cov = list(cov)
    if n_EZmocks is not None:
        if n_EZmocks > len(cov):
            raise ValueError(f"Requested n_EZmocks={n_EZmocks} exceeds available {len(cov)} EZmocks!")
        print(f'Using only first {n_EZmocks} EZmocks for covariance estimation ...')
        cov = cov[:n_EZmocks] 
    return data, cov

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

def prepare_theory(
    z: float,
    cosmology: str='DESI',
    mode: str='b-p',
    fnl: float=0,
    priors: dict[str, list]=dict(),
    fix_fNL: bool=True,
) -> PNGTracerPowerSpectrumMultipoles:
    """
    fnl: fNL value to fix, if fix_fNL is True.
    """
    
    template = FixedPowerSpectrumTemplate(z=z, fiducial=cosmology)
    # fnl_loc is degenerate with PNG bias bphi. Parameterization is controlled by "mode".
    # - "b-p": bphi = 2 * 1.686 * (b1 - p), p as a parameter
    # - "bphi": bphi as a parameter
    # - "bfnl_loc": bfnl_loc = bphi * fnl_loc as a parameter'
    theory = PNGTracerPowerSpectrumMultipoles(template=template, mode=mode)
    
    ## fixed fNL
    if fix_fNL:
        theory.init.params['fnl_loc'].update(value=fnl, fixed=True) 

    ## other parameters may need larger prior ranges
    for key in priors:
        theory.init.params[key].update(fixed=False, prior=priors[key])
    return theory

def bestfit_p_inference(
    theory: PNGTracerPowerSpectrumMultipoles,
    data,
    cov,
    ells: list[int] =[0],
    k: np.ndarray | list[np.ndarray] | None = None,
    klim: dict = {0: [0.005, 0.2, 0.005]},
) -> dict:
    """
    Use Minuit Profiler to find bestfit parameters.
    Data: monopole power spectrum from mocks.
    Covariance: provided covariance matrix.
    k: if one only provided simple arrays for data and covariance, one can provide the corresponding (list of) k wavenumbers as a (list of) array k.
    """
    observable = TracerPowerSpectrumMultipolesObservable(data=data, covariance=cov, ells=ells, k=k, klim=klim, theory=theory)
    
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


    ## bestfit
    # best_p = profiles.bestfit.choice(input=True)['p'].value
    bestfit_dict = {}
    for key in theory.all_params:
        bestfit_value = profiles.bestfit.choice(input=True)[str(key)].value
        # theory.init.params[key].update(value=bestfit_value)
        bestfit_dict[str(key)] = bestfit_value
    # best_p = bestfit_dict['p']
    return bestfit_dict