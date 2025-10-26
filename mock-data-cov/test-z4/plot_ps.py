# !/usr/bin/env python3
# the workdir is ~/projects/fihobi/mock-data-cov/
# pypower requires `source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main` on NERSC

import numpy as np
import glob
from pypower import PowerSpectrumMultipoles
from matplotlib import pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')
color = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Data -------------------------------------------------------------------------

dir_rp6s11='/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks_test/Abacus_pngbase_c300_ph000/z2.000/galaxies_rsd_dv/'
dir_base='/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks/Abacus_pngbase_c300_ph000/z2.000/galaxies_rsd/'
dir_dv='/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks/Abacus_pngbase_c300_ph000/z2.000/galaxies_rsd_dv/'
poles_base = PowerSpectrumMultipoles.load(dir_base + 'pypower_poles.npy')
poles_rp6s11 = PowerSpectrumMultipoles.load(dir_rp6s11 + 'pypower_poles.npy')
poles_dv = PowerSpectrumMultipoles.load(dir_dv + 'pypower_poles.npy')
kb, Pb = poles_base(ell=0, return_k=True, complex=False)
kd, Pd = poles_dv(ell=0, return_k=True, complex=False)
kr, Pr = poles_rp6s11(ell=0, return_k=True, complex=False)
# directly add dv
poles300_qso_dv = PowerSpectrumMultipoles.load('/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks/Abacus_pngbase_c300_ph000/z2.000/galaxies_rsd_dv/ps_n256.npy')
kb_adv, Pb_adv = poles300_qso_dv(ell=0, return_k=True, complex=False)

## EZmocks
# files = glob.glob('/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z4_c300/pypowerpoles_seed*.npz')
files = glob.glob('/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z4_c300/pypowerpoles_r*.npy')
# 不排序，直接按 glob 返回的顺序遍历所有文件
p0_ez = []
for fn in files:
    # data = np.load(fn, allow_pickle=True)
    # poles = data['poles'].item()  # PowerSpectrumMultipoles object
    poles = PowerSpectrumMultipoles.load(fn) 
    k, p0 = poles(ell=0, return_k=True, complex=False)
    p0_ez.append(p0)
p0_ez_avg = np.mean(p0_ez, axis=0)
    
    
# Plot -------------------------------------------------------------------------

fig, axs = plt.subplots(2,1,constrained_layout=True,sharex='col',figsize=(8,8),gridspec_kw={'height_ratios': [3, 1]})

# top panel: EZmocks
p = p0_ez[0]
axs[0].plot(k, p, color='gray', alpha=0.3, label='EZmock')
for p in p0_ez[1:]:
    axs[0].plot(k, p, color='gray', alpha=0.3)
axs[0].plot(k, p0_ez_avg, color='black', lw=2, label='EZmock average')
# top panel: original spectra
axs[0].plot(kb, Pb, label='base', color=color[0])
axs[0].plot(kd, Pd, '--', label='dv', color=color[1])
axs[0].plot(kr, Pr, ':', label='rp6s11', color=color[2])
axs[0].plot(kb_adv, Pb_adv, '-.', label='directly add dv to base', color=color[3])
axs[0].set_xscale('log')
axs[0].set_yscale('log')
axs[0].set_ylabel(r'$P_0(k)$ [$(\mathrm{Mpc}/h)^{3}$]')
axs[0].legend()

# bottom panel: fractional errors (P_variant - P_base) / P_base
frac_ez = (p0_ez_avg - Pb) / Pb
frac_dv = (Pd - Pb) / Pb
frac_rp = (Pr - Pb) / Pb
frac_adv = (Pb_adv - Pb) / Pb

axs[1].axhline(0, color='gray', lw=0.8)
axs[1].plot(k, frac_ez, color='black', lw=2)
axs[1].plot(kb, frac_dv, '--', color=color[1])
axs[1].plot(kb, frac_rp, ':', color=color[2])
axs[1].plot(kb, frac_adv, '-.', color=color[3])
axs[1].set_xscale('log')
axs[1].set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
axs[1].set_ylabel(r'$(P_{\rm xx}-P_{\rm base})/P_{\rm base}$')
# set sensible symmetric y-limits based on data
m = np.nanmax(np.abs(np.hstack([frac_ez, frac_dv, frac_rp])))
ylim = max(0.01, m * 1.2)
axs[1].axhspan(-0.05, 0.05, color='gray', alpha=0.5, label="5% error")
axs[1].axhspan(-0.1, 0.1, color='gray', alpha=0.3)
axs[1].set_ylim(-ylim, ylim)
axs[1].legend(loc='upper right')
plt.tight_layout()
plt.savefig('test-z4/ps_comparison.png', dpi=300)