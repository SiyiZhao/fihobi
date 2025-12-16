import numpy as np
from desilike.theories.galaxy_clustering import FixedPowerSpectrumTemplate, PNGTracerPowerSpectrumMultipoles
from desilike.observables.galaxy_clustering import TracerPowerSpectrumMultipolesObservable
from desilike.likelihoods import ObservablesGaussianLikelihood

from desilike.profilers import MinuitProfiler


def prepare_theory_fix_fNL(
    z: float,
    cosmology: str='DESI',
    mode: str='b-p',
    fnl: float=0,
    priors: dict[str, list]=dict(),
):
    
    template = FixedPowerSpectrumTemplate(z=z, fiducial=cosmology)
    # fnl_loc is degenerate with PNG bias bphi. Parameterization is controlled by "mode".
    # - "b-p": bphi = 2 * 1.686 * (b1 - p), p as a parameter
    # - "bphi": bphi as a parameter
    # - "bfnl_loc": bfnl_loc = bphi * fnl_loc as a parameter'
    theory = PNGTracerPowerSpectrumMultipoles(template=template, mode=mode)
    
    ## fixed fNL
    theory.init.params['fnl_loc'].update(value=fnl, fixed=True) 

    ## other parameters may need larger prior ranges
    # priors = config.get('prior', {})
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