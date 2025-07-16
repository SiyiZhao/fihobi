# This script compares the xi0 and xi2 from the mock and the data.

# %%
import numpy as np
import yaml
from matplotlib import pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')

# %%
path2config = 'config/y3_lrg_smu.yaml'
config = yaml.safe_load(open(path2config))

# %%
path2data = '/global/homes/s/siyizhao/projects/fihobi/data/l/mocks_y3_xi0_bestfit/xi0_LRG.txt'
xi0_mock = np.loadtxt(path2data)
path2data = '/global/homes/s/siyizhao/projects/fihobi/data/l/mocks_y3_xi0_bestfit/xi2_LRG.txt'
xi2_mock = np.loadtxt(path2data)

# %% [markdown]
# ## Reference

# %%
data_params = config['data_params']
path2power = data_params['tracer_combos']['LRG_LRG']['path2power']
path2cov = data_params['tracer_combos']['LRG_LRG']['path2cov']
data = np.loadtxt(path2power)
sep = data[:, 0]
xi0 = data[:, 1]
xi2 = data[:, 2]
cov = np.load(path2cov)
xi0err = np.sqrt(np.diag(cov))

# %%
path = '/global/homes/s/siyizhao/data/Y3/loa-v1/hodfit/cov_xi2_LRG_GCcomb_0.6_0.8_pip_angular_bitwise_log_njack128_nran4_split20.npy'
cov22 = np.load(path)
xi2err = np.sqrt(np.diag(cov22))

# %% [markdown]
# ## Plot

# %%
fig, axs = plt.subplots(2, 1, figsize=(7, 7), sharex=True, gridspec_kw={'height_ratios': [2, 1], 'hspace': 0})

# 上图
axs[0].errorbar(sep, sep**2*xi0, yerr=sep**2*xi0err, fmt='o', label=r'$\xi_0$ measured', mfc='none', color='C0')
axs[0].plot(sep, sep**2*xi0_mock, 'x', label=r'$\xi_0$ hodfitting', color='C0')
axs[0].errorbar(sep, sep**2*xi2, yerr=sep**2*xi2err, fmt='o', label=r'$\xi_2$ measured', mfc='none', color='C1')
axs[0].plot(sep, sep**2*xi2_mock, 'x', label=r'$\xi_2$ mock', color='C1')
axs[0].set_ylabel(r'$s^2 \xi_l [({\rm Mpc}/h)^{-1}]$')
axs[0].set_xscale('log')
axs[0].set_yscale('symlog')
axs[0].legend()
axs[0].grid(True, which='both', ls=':')

# 下图
sigma = (xi0_mock - xi0) / xi0err
axs[1].plot(sep, sigma, 'o-', color='C0')
# axs[1].plot(sep, sigma, 'o-', label=r'$\xi_0$', color='C0')
sigma_xi2 = (xi2_mock - xi2) / xi2err
axs[1].plot(sep, sigma_xi2, 'o-', color='C1')
# axs[1].plot(sep, sigma_xi2, 'o-', label=r'$\xi_2$', color='C1')
axs[1].axhline(0, ls='--', color='gray')
axs[1].axhspan(-1, 1, color='gray', alpha=0.7, label='1$\sigma$ region')
axs[1].axhspan(-3, 3, color='gray', alpha=0.5, label='3$\sigma$ region')
axs[1].set_xscale('log')
axs[1].set_xlabel(r'$s [{\rm Mpc}/h]$')
axs[1].set_ylabel(r'$(\xi_l^{\rm mock} - \xi_l^{\rm data})/\sigma$')
axs[1].grid(True, which='both', ls=':')

plt.tight_layout()
plt.legend()
plt.savefig('plot/xi0_xi2_comparison.png', dpi=300)

# %%



