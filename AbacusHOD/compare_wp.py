# %%
import numpy as np
import yaml
from matplotlib import pyplot as plt

# %%
aHOD_dir = '/pscratch/sd/s/siyizhao/fihobi/mocks/'

# %%
wp = [1260.64041083,  827.44231474,  528.56093459,  330.29807753,
        205.96155382,  133.72149709,   97.39522361,   73.80377416,
         55.43015369,   40.43294778,   28.61688253,   19.2606093 ,
         12.05349031,    6.7478916 ]

# %%
path2config = 'config/abacus_hod.yaml'
config = yaml.safe_load(open(path2config))
clustering_params = config['clustering_params']
bin_params = clustering_params['bin_params']
rpbins = np.logspace(bin_params['logmin'], bin_params['logmax'], bin_params['nbins']+1)

# %%
rpbin_mid = 0.5 * (rpbins[1:] + rpbins[:-1])

# %%
rpbin_logmid = 10**( ( np.log10(rpbins[1:]) + np.log10(rpbins[:-1]) ) / 2 )

# %% [markdown]
# ## Yuan et al. 2024 data (Zenodo)

# %%
zenodo_dir = '/global/homes/s/siyizhao/projects/fihobi/data/l/data4zenodo/'
wp_path = zenodo_dir + 'LRG_main_z0608_wp.dat'
data = np.loadtxt(wp_path)
rp_yuan = data[:, 0]
wp_yuan = data[:, 1]
wp_cov = np.loadtxt(zenodo_dir + 'LRG_main_z0608_wpcov.dat')
wp_yuan_err = np.sqrt(np.diag(wp_cov))

# %%
np.log10(rp_yuan[1:]) - np.log10(rp_yuan[:-1])

# %% [markdown]
# ## Plot

# %%
plt.errorbar(rp_yuan, rp_yuan*wp_yuan, yerr=rp_yuan*wp_yuan_err, fmt='o', label='Yuan et al. 2024')
plt.plot(rpbin_mid, rpbin_mid*wp, '.', label='my run')
plt.plot(rpbin_logmid, rpbin_logmid*wp, 'o', label='my run (log mid)')
plt.xlabel(r'$r_p [{\rm Mpc}/h]$')
plt.ylabel(r'$r_p w_p [({\rm Mpc}/h)^{-2}]$')
plt.xscale('log')
plt.xlim(0.1, 35)
plt.ylim(110, 230)
plt.legend()
plt.savefig('plot/wp.png', dpi=300)


