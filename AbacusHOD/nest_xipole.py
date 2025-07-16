#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a script for running nested sampling to fit monopole on HOD mock catalogs.

Refer: abacusutils/scripts/hod/run_nested.py

Usage
-----
$ python ./nest_xipole.py --help
"""

import argparse
import os

import dill
import numpy as np
import yaml
from dynesty import NestedSampler
from scipy import stats

from abacusnbody.hod.abacus_hod import AbacusHOD

DEFAULTS = {}
DEFAULTS['path2config'] = 'config/y3_lrg_smu.yaml'

class ObsData:
    """A class to hold observed data and covariance matrix for fitting.
    """

    def __init__(self, data, cov, ngal=None, ngal_std=None):
        """Initialize with observed data and covariance matrix. Optional number density and its standard deviation."""
        self.data = data
        self.cov = cov
        self.ngal = ngal
        self.ngal_std = ngal_std

    def compute_likelihood(self, theory_density):
        """Compute the likelihood of the observed data given the theory density."""
        # for number 
        n_mock = theory_density['ngal']
        n_data = self.ngal
        sigma_n = self.ngal_std
        if n_mock >= n_data:
            chi_n = 0
        else:
            chi_n = ( (n_data - n_mock)  / sigma_n ) ** 2  
            
        # Here we assume a Gaussian likelihood for simplicity
        diff = self.data - theory_density['clustering']
        inv_cov = np.linalg.inv(self.cov)
        chi_clustering = np.dot(diff.T, np.dot(inv_cov, diff))
        
        # total chi-squared
        chi = chi_clustering + chi_n
        lnP = -0.5 * chi
        return lnP

def lnprob(p, param_mapping, param_tracer, Data, Ball):
    # read the parameters
    for key in param_mapping.keys():
        mapping_idx = param_mapping[key]
        tracer_type = param_tracer[key]
        Ball.tracers[tracer_type][key] = p[mapping_idx]

    # pass them to the mock dictionary
    mock_dict = Ball.run_hod(Ball.tracers, Ball.want_rsd, Nthread=Nthread)

    # measure the mock
    theory_density = {}
    # clustering = Ball.compute_wp(
    #     mock_dict, Ball.rpbins, Ball.pimax, Ball.pi_bin_size, Nthread=Nthread
    # )
    # sbins = Ball.rpbins
    clustering = Ball.compute_multipole(
        mock_dict, Ball.rpbins, Ball.pi_bin_size, orders=[0], Nthread=Nthread
    )
    
    NgalDict, FsatDict = Ball.compute_ngal(Ball.tracers, Nthread=Nthread)
    
    # nbins = Ball.nbins
    # theory_density['clustering'] = clustering['LRG_LRG'][nbins:nbins+nbins]  # xi0 in old AbacusHOD version
    theory_density['clustering'] = clustering['LRG_LRG']  # xi0
    boxV = Ball.lbox ** 3  # volume of the box in (Mpc/h)^3  
    theory_density['ngal'] = NgalDict['LRG'] / boxV
    lnP = Data.compute_likelihood(theory_density) 
    
    return lnP


# prior transform function
def prior_transform(u, params):
    """Transforms the uniform random variables `u ~ Unif[0., 1.)`
    to the parameters of interest. Truncated Normal distribution is used here."""    
    m = params[:,0] # params_hod
    s = params[:,3] # params_hod_initial_range
    low = params[:,1]
    high = params[:,2]
    # x = stats.norm.ppf(u, loc=params_hod, scale=params_hod_initial_range)
    low_n, high_n = (low - m) / s, (high - m) / s  # standardize
    x = stats.truncnorm.ppf(u, low_n, high_n, loc=m, scale=s)
    return x


def ReadData(data_params, HOD_params):
    """
    Read the observed data and covariance matrix for the LRG_LRG tracer combo.
    """
    path2power = data_params['tracer_combos']['LRG_LRG']['path2power']
    path2cov = data_params['tracer_combos']['LRG_LRG']['path2cov']
    
    data = np.loadtxt(path2power)
    # sep = data[:, 0]
    xi0 = data[:, 1]
    cov = np.load(path2cov)
    
    ## read the number density and its standard deviation
    density_mean = data_params['tracer_density_mean']['LRG']
    density_std = data_params['tracer_density_std']['LRG']
    
    ## define the reference data
    RefData = ObsData(data=xi0, cov=cov, ngal=density_mean, ngal_std=density_std)
    return RefData


def main(path2config):
    
    # load the yaml parameters
    config = yaml.safe_load(open(path2config))
    sim_params = config['sim_params']
    HOD_params = config['HOD_params']
    clustering_params = config['clustering_params']
    data_params = config['data_params']
    dynesty_config_params = config['dynesty_config_params']
    fit_params = config['dynesty_fit_params']
    print('config loaded')

    # create a new abacushod object and load the subsamples
    newBall = AbacusHOD(sim_params, HOD_params, clustering_params)

    # read data parameters
    newData = ReadData(data_params, HOD_params) 
    print('data loaded') 
    
    # more parameters for xi multipole
    # newBall.mu_bin_size = clustering_params['mu_bin_size']
    # bin_params = clustering_params['bin_params']
    # newBall.nbins = bin_params['nbins']

    # parameters to fit
    nparams = len(fit_params.keys())
    param_mapping = {}
    param_tracer = {}
    params = np.zeros((nparams, 4))  # [mean, min, max, std]
    for key in fit_params.keys():
        mapping_idx = fit_params[key][0]
        tracer_type = fit_params[key][-1]
        param_mapping[key] = mapping_idx
        param_tracer[key] = tracer_type
        params[mapping_idx, :] = fit_params[key][1:-1]
    print('parameters to fit:', fit_params)
    
    # Make path to output
    if not os.path.isdir(os.path.expanduser(dynesty_config_params['path2output'])):
        try:
            os.makedirs(os.path.expanduser(dynesty_config_params['path2output']))
        except KeyError:
            pass

    # dynesty parameters
    nlive = dynesty_config_params['nlive']
    maxcall = dynesty_config_params['maxcall']
    method = dynesty_config_params['method']
    rseed = dynesty_config_params['rseed']
    # bound = dynesty_config_params['bound']

    # where to record
    prefix_chain = os.path.join(
        os.path.expanduser(dynesty_config_params['path2output']),
        dynesty_config_params['chainsPrefix'],
    )

    # initiate & run sampler
    found_file = os.path.isfile(prefix_chain + '.dill')
    if (not found_file) or (not dynesty_config_params['rerun']):
        # initialize our nested sampler
        sampler = NestedSampler(
            lnprob,
            prior_transform,
            nparams,
            logl_args=[param_mapping, param_tracer, newData, newBall],
            ptform_args=[params],
            nlive=nlive,
            sample=method,
            rstate=np.random.default_rng(rseed),
        )
        print('sampler initialized')
    # first_update = {'min_eff': 20})

    else:
        # load sampler to continue the run
        with open(prefix_chain + '.dill', 'rb') as f:
            sampler = dill.load(f)
        # sampler.rstate = np.load(prefix_chain + '_results.npz', allow_pickle=True)['rstate']
        print('sampler loaded from file')
    print('run sampler')

    sampler.run_nested(maxcall=maxcall)
        
        
    # save sampler itself
    with open(prefix_chain + '.dill', 'wb') as f:
        dill.dump(sampler, f)
    res1 = sampler.results
    np.savez(prefix_chain + '_results.npz', res=res1, rstate=np.random.get_state())


class ArgParseFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


if __name__ == '__main__':
    Nthread = os.cpu_count()
    print("Number of threads set to:", Nthread)

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=ArgParseFormatter
    )
    parser.add_argument(
        '--path2config',
        dest='path2config',
        type=str,
        help='Path to config file.',
        default=DEFAULTS['path2config'],
    )
    
    args = vars(parser.parse_args())
    print('args:', args)
    main(**args)
