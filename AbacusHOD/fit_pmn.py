#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a script for running pymultinest sampling to fit multipoles on HOD mock catalogs.

Refer: abacusutils/scripts/hod/run_nested.py

Usage
-----
$ python ./fit_pmn.py --help
"""

import argparse
import os

import numpy as np
import yaml
from scipy import stats

from abacusnbody.hod.abacus_hod import AbacusHOD
from mypmn import my_pmn

# from abacusnbody.hod.utils import setup_logging
# setup_logging()

DEFAULTS = {}
DEFAULTS['path2config'] = 'config/y3_lrg_smu.yaml'

class ObsData:
    """A class to hold observed data and covariance matrix for fitting.
    """

    def __init__(self, data, cov, ngal=None, ngal_std=None):
        """Initialize with observed data and covariance matrix. Optional number density and its standard deviation."""
        self.data = data
        self.cov = cov
        self.icov = np.linalg.inv(cov)  # inverse covariance matrix
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
        chi_clustering = np.dot(diff.T, np.dot(self.icov, diff))
        
        # total chi-squared
        chi = chi_clustering + chi_n
        lnP = -0.5 * chi
        return lnP

# def generate_nfw_random_numbers(size=1000000, x_min=0.01, x_max=100.0):
#     """
#     生成从 NFW 轮廓采样的随机数
    
#     Parameters
#     ----------
#     size : int
#         要生成的随机数数量
#     x_min : float
#         最小 x 值，默认 0.01
#     x_max : float
#         最大 x 值，默认 100.0
        
#     Returns
#     -------
#     np.array
#         从 NFW 轮廓采样的随机数数组
#     """
    
#     def nfw_pdf(x):
#         """NFW 概率密度函数 P(x) = x² / (x*(1+x)²) = x / (1+x)²"""
#         return x / (1 + x)**2
    
#     def nfw_cdf(x):
#         """NFW 累积分布函数的解析解"""
#         return x / (1 + x)
    
#     def nfw_cdf_normalized(x, norm_factor):
#         """归一化的 CDF"""
#         return nfw_cdf(x) / norm_factor
    
#     def inverse_cdf(u, norm_factor):
#         """CDF 的逆函数，用于逆变换采样"""
#         # 解方程: u = x/(1+x) / norm_factor
#         # 即: u * norm_factor = x/(1+x)
#         # 解得: x = u * norm_factor / (1 - u * norm_factor)
#         y = u * norm_factor
#         if y >= 1.0:
#             return x_max
#         return y / (1 - y)
    
#     # 计算归一化因子
#     norm_factor = nfw_cdf(x_max) - nfw_cdf(x_min)
    
#     # 生成均匀分布的随机数
#     u = np.random.uniform(0, 1, size)
    
#     # 调整 u 值到 [CDF(x_min), CDF(x_max)] 范围
#     u_adjusted = nfw_cdf(x_min) / norm_factor + u * (1 - nfw_cdf(x_min) / norm_factor)
    
#     # 使用逆变换方法生成 NFW 分布的随机数
#     samples = np.array([inverse_cdf(ui, norm_factor) for ui in u_adjusted])
    
#     # 确保样本在指定范围内
#     samples = np.clip(samples, x_min, x_max)
    
#     return samples.astype(np.float32)

def lnprob(p, param_mapping, param_tracer, Data, Ball):
    # read the parameters
    for key in param_mapping.keys():
        mapping_idx = param_mapping[key]
        tracer_type = param_tracer[key]
        Ball.tracers[tracer_type][key] = p[mapping_idx]

    # pass them to the mock dictionary
    # NFW_draw = generate_nfw_random_numbers(size=1000000)
    # mock_dict = Ball.run_hod(Ball.tracers, Ball.want_rsd, want_nfw=True, NFW_draw=NFW_draw, Nthread=Nthread)
    mock_dict = Ball.run_hod(Ball.tracers, Ball.want_rsd, Nthread=Nthread)
    
    # measure the mock
    theory_density = {}
    # clustering = Ball.compute_wp(
    #     mock_dict, Ball.rpbins, Ball.pimax, Ball.pi_bin_size, Nthread=Nthread
    # )
    # # sbins = Ball.rpbins
    # clustering = Ball.compute_multipole(
    #     mock_dict, Ball.rpbins, Ball.pi_bin_size, orders=[0, 2], Nthread=Nthread
    # )
    wp = Ball.compute_wp(mock_dict, rpbins, pimax, pi_bin_size, Nthread=Nthread)
    multipole = Ball.compute_multipole(
        mock_dict, sbins, nbins_mu, orders=[0, 2], Nthread=Nthread
    )
    
    NgalDict, FsatDict = Ball.compute_ngal(Ball.tracers, Nthread=Nthread)
    
    # nbins = Ball.nbins
    # theory_density['clustering'] = clustering['LRG_LRG'][nbins:nbins+nbins]  # xi0 in old AbacusHOD version
    # theory_density['clustering'] = clustering['LRG_LRG']  # xi0,xi2
    theory_density['clustering'] = np.concatenate((wp['LRG_LRG'], multipole['LRG_LRG']))  # wp, xi0, xi2
    boxV = Ball.lbox ** 3  # volume of the box in (Mpc/h)^3  
    theory_density['ngal'] = NgalDict['LRG'] / boxV
    lnP = Data.compute_likelihood(theory_density) 
    
    return lnP


def ReadData(data_params):
    """
    Read the observed data and covariance matrix for the LRG_LRG tracer combo.
    """
    # path2power = data_params['tracer_combos']['LRG_LRG']['path2power']
    # path2cov = data_params['tracer_combos']['LRG_LRG']['path2cov']
    
    # data = np.loadtxt(path2power)
    # # sep = data[:, 0]
    # xi0 = data[:, 1]
    # xi2 = data[:, 2]
    # # data = xi0  # only monopole is used for HOD fitting
    # data = np.hstack((xi0, xi2))
    # cov = np.load(path2cov)
    
    import h5py
    
    path2data = data_params['tracer_combos']['LRG_LRG']['path2data']
    z='z0'  # assuming the data is for redshift z0=0.5 (0.4-0.6), change as needed
    with h5py.File(path2data, 'r') as f:
        group = f[z]
        data = group['data_vector'][:]
        cov = group['cov'][:]
            
    ## read the number density and its standard deviation
    density_mean = data_params['tracer_density_mean']['LRG']
    density_std = data_params['tracer_density_std']['LRG']
    
    ## define the reference data
    RefData = ObsData(data=data, cov=cov, ngal=density_mean, ngal_std=density_std)
    return RefData



class ArgParseFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


if __name__ == '__main__':
    Nthread = 64  # Number of threads to use, should be 1-64

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
    path2config = args['path2config']
    
    
        
    # load the yaml parameters
    config = yaml.safe_load(open(path2config))
    sim_params = config['sim_params']
    HOD_params = config['HOD_params']
    clustering_params = config['clustering_params']
    data_params = config['data_params']
    pmn_config_params = config['pmn_config_params']
    fit_params = config['pmn_fit_params']
    print('config loaded')

    # create a new abacushod object and load the subsamples
    newBall = AbacusHOD(sim_params, HOD_params, clustering_params)

    # read data parameters
    newData = ReadData(data_params) 
    print('data loaded') 
    
    # more parameters for xi multipole
    # newBall.mu_bin_size = clustering_params['mu_bin_size']
    # bin_params = clustering_params['bin_params']
    # newBall.nbins = bin_params['nbins']
    # parameters for clustering
    rp_bin_params = clustering_params['bin_params']
    wp_num = rp_bin_params['nbins']
    rpbins = np.logspace(rp_bin_params['logmin'], rp_bin_params['logmax'], wp_num+1)
    pimax = clustering_params['pimax']
    pi_bin_size = clustering_params['pi_bin_size']    # the pi binning is configrured by pi_max and bin size
    sbin_params = clustering_params['sbin_params']
    xi_num = sbin_params['nbins']
    sbins = np.logspace(sbin_params['logmin'], sbin_params['logmax'], xi_num+1)
    nbins_mu = clustering_params['mu_bin_size']  


    # parameters to fit
    nparams = len(fit_params.keys())
    param_mapping = {}
    param_tracer = {}
    params = np.zeros((nparams, 4))  # [mean, min, max, std]
    
    params_range = {}
    for key in fit_params.keys():
        mapping_idx = fit_params[key][0]
        tracer_type = fit_params[key][-1]
        param_mapping[key] = mapping_idx
        param_tracer[key] = tracer_type
        params[mapping_idx, :] = fit_params[key][1:-1]
        params_range[key] = fit_params[key][2:4]
    print('parameters to fit:', fit_params)
    # # prior transform function
    # def prior_transform(u, ndim, nparam, params=params):
    #     """Transforms the uniform random variables `u ~ Unif[0., 1.)`
    #     to the parameters of interest. Truncated Normal distribution is used here."""    
    #     m = params[:,0] # params_hod
    #     s = params[:,3] # params_hod_initial_range
    #     low = params[:,1]
    #     high = params[:,2]
    #     # x = stats.norm.ppf(u, loc=params_hod, scale=params_hod_initial_range)
    #     low_n, high_n = (low - m) / s, (high - m) / s  # standardize
    #     u = stats.truncnorm.ppf(u, low_n, high_n, loc=m, scale=s)

    def lnprior(p, params):
        """Compute the log-prior for the given parameters."""
        # lnprior_value = 0.0
        # for i in range(nparams):
        #     mean, low, high, std = params[i]
        #     if p[i] < low or p[i] > high:
        #         return -np.inf
        #     # Here we assume Gaussian prior
        #     lnprior_value -= (p[i]-mean) ** 2 / (2 * std ** 2)
            # lnprior_value += stats.norm.logpdf(p[i], loc=mean, scale=std)
        mean = params[:, 0]
        std = params[:, 3]
        lnG = - (p - mean) ** 2 / (2 * std ** 2)
        lnprior_value = np.sum(lnG)
        return lnprior_value
            
    
    def log_likelihood(p):
        """Compute the log-likelihood for the given parameters."""
        return lnprob(p, param_mapping, param_tracer, newData, newBall) + lnprior(p, params)
    
    # Make path to output
    path2output = pmn_config_params['path2output']
    # if not os.path.isdir(os.path.expanduser(path2output)):
    #     try:
    #         os.makedirs(os.path.expanduser(path2output))
    #     except KeyError:
    #         pass

    # pmn parameters
    chain_prefix = pmn_config_params['chainsPrefix']
    nlive = pmn_config_params['nlive']
    tol  = pmn_config_params['tol']
    labels = [r"\log M_{\text{cut}}", r"\log M_1", r"\sigma", r"\alpha", r"\kappa", r"\alpha_{\text{c}}", r"\alpha_{\text{s}}"]
        
    ## define the multinest class
    fit_ = my_pmn(params_range, log_likelihood, path2output, filename=chain_prefix, param_label=labels, live_points=nlive, tol=tol)

    ## prepare the output directory 
    fit_.write_prior_file()

    ## run 
    # fit_.run_pmn(prior_transform=prior_transform)
    ## test
    # test = log_likelihood(np.array([12.0, 13.0, 0.5, 1.0, 0.1, 0 ,1 ]))  # example call
    # print(test)
    fit_.run_pmn()

    ## plot
    fit_.plot_result(plot_path=pmn_config_params['plot'])

    print('Finished fitting! Take a break!')
    