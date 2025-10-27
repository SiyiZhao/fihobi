import numpy as np
from pypower import PowerSpectrumMultipoles
from matplotlib import pyplot as plt
import os

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