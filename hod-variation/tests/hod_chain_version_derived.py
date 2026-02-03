import numpy as np
import matplotlib.pyplot as plt
from getdist import loadMCSamples, plots
import matplotlib as mpl
mpl.rc_file('/global/homes/s/siyizhao/projects/fihobi/fig/matplotlibrc')

import os, sys
sys.path.insert(0, os.path.abspath('../../src'))
from chain_helper import chain


def compare_chain(fn_all, no_param=[], labels=['chain1', 'chain2'], colors=['red', 'blue'], limit_param=False, out='triangle_plot.png'):
    samples_all = []
    params = []
    param_limits = {}
    bestfits = {}
    for fn in fn_all:
        samples = loadMCSamples(fn)
        samples_all.append(samples)
        # Get parameter names and update limits
        pnames = samples.getParamNames().list()
        for name in pnames:
            if name in no_param:
                continue
            if name not in params:
                params.append(name)
                bestfits[name] = []
        if limit_param==True:
            for name in params:
                # Update parameter limits
                lo, hi = samples.getLower(name), samples.getUpper(name)
                if name in param_limits:
                    cur_lo, cur_hi = param_limits[name]
                    param_limits[name] = (min(cur_lo, lo), max(cur_hi, hi))
                else:
                    param_limits[name] = (lo, hi)
    g = plots.get_subplot_plotter()
    g.settings.legend_fontsize = 30
    g.settings.axes_labelsize = 30
    g.settings.axes_fontsize = 20
    g.settings.linewidth_contour = 2.0   # 改 contour 线条宽度
    g.settings.linewidth = 2.0           # 改 1D 曲线的线宽
    marker_args = [{'color': color, 'linestyle': '--', 'linewidth': 3.0, 'label': labels[i]+' - MAP'} for i, color in enumerate(colors)]
    g.triangle_plot(
        samples_all,
        params=params,
        param_limits=param_limits,
        filled=False,
        contour_colors=colors,
        markers=bestfits,
        marker_args=marker_args,
        legend_labels=labels,
        legend_loc='upper right',
    )
    plt.savefig(out)
    print(f'[plot] triangle plot -> {out}')
    plt.clf()


def logsigma(params):
    sigma = params[2]
    return np.log10(sigma)

def flat_sigma(params):
    logsigma = params[2]
    return 10**logsigma

def logalpha_c(params):
    alpha_c = params[5]
    return np.log10(alpha_c)

def logalpha_s(params):
    alpha_s = params[6]
    return np.log10(alpha_s)

def unit_sigma(params):
    return params[2]

def unit_alpha_c(params):
    return params[5]

def unit_alpha_s(params):
    return params[6]
    
    
if __name__ == "__main__":
    parent_dir = '/pscratch/sd/s/siyizhao/desi-dr2-hod/'
    ### LRGs HODv3 and HODv4
    for ztag in ['z1', 'z2', 'z3']:
        chain_v3 = chain(outdir=parent_dir+f'loa-v2_HODv3/LRG-fnl100/{ztag}_base-A/', filename='/chain_v3_')
        chain_v3.read_pmn()
        chain_v3.derive_new_params(derive_func=flat_sigma, new_para='flat_sigma', new_para_label='\sigma', filename='/chain_v3_flat_sigma_')
        chain_v4 = chain(outdir=parent_dir+f'loa-v2_HODv4/LRG-fnl100/{ztag}_base-A/', filename='/chain_v4_')
        chain_v4.read_pmn()
        chain_v4.derive_new_params(derive_func=unit_sigma, new_para='flat_sigma', new_para_label='\sigma', filename='/chain_v4_flat_sigma_')
        fn_all = [
            parent_dir+f'loa-v2_HODv3/LRG-fnl100/{ztag}_base-A/chain_v3_flat_sigma_',
            parent_dir+f'loa-v2_HODv4/LRG-fnl100/{ztag}_base-A/chain_v4_flat_sigma_',
        ]
        compare_chain(fn_all, no_param=['sigma'], labels=[f'HODv3, {ztag}, base-A, log sigma sampling, derived sigma', f'HODv4, {ztag}, base-A, flat sigma sampling'], colors=['red', 'blue'], out=f'../output/HODv3_v4_LRG_{ztag}.png')    
    
    
    # ### LRG1
    # chain_A = chain(outdir='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/LRG-fnl100/z1_base-A/', filename='/chain_v3_')
    # chain_A.read_pmn()
    # chain_A.derive_new_params(derive_func=logalpha_c, new_para='log_alpha_c', new_para_label='\log \\alpha_c', filename='/chain_v3_derived_')
    # chain_A.derive_new_params(derive_func=logalpha_s, new_para='log_alpha_s', new_para_label='\log \\alpha_s', filename='/chain_v3_derived_')
    # chain_dv = chain(outdir='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv2/LRG-fnl100/z1_base-A-dv/', filename='/chain_v2_')
    # chain_dv.read_pmn()
    # chain_dv.derive_new_params(derive_func=unit_alpha_c, new_para='log_alpha_c', new_para_label='\log \\alpha_c', filename='/chain_v2_derived_')
    # chain_dv.derive_new_params(derive_func=unit_alpha_s, new_para='log_alpha_s', new_para_label='\log \\alpha_s', filename='/chain_v2_derived_')
    # fn_all = [
    #     '/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv2/LRG-fnl100/z1_base-A-dv/chain_v2_derived_',
    #     '/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/LRG-fnl100/z1_base-A/chain_v3_derived_',
    # ]
    # compare_chain(fn_all, labels=['HODv2, base-A-dv', 'HODv3, base-A'], colors=['red', 'blue'], out='../output/HOD_dv_LRG1.pdf')
    
    # ### QSO6
    # chain_A = chain(outdir='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/QSO-fnl100/z6_base-A/', filename='/chain_v3_') #alpha_c & sigma
    # chain_A.read_pmn()
    # chain_A.derive_new_params(derive_func=logsigma, new_para='log_sigma', new_para_label='\log \sigma', filename='/chain_v3_derived_')
    # chain_A.derive_new_params(derive_func=logalpha_c, new_para='log_alpha_c', new_para_label='\log \\alpha_c', filename='/chain_v3_derived_')
    # chain_dv = chain(outdir='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv2/QSO-fnl100/z6_base-A-dv/', filename='/chain_v2_') #alpha_c & sigma
    # chain_dv.read_pmn()
    # chain_dv.derive_new_params(derive_func=unit_sigma, new_para='log_sigma', new_para_label='\log \sigma', filename='/chain_v2_derived_')
    # chain_dv.derive_new_params(derive_func=unit_alpha_c, new_para='log_alpha_c', new_para_label='\log \\alpha_c', filename='/chain_v2_derived_')
    # fn_all = [
    #     '/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv2/QSO-fnl100/z6_base-A-dv/chain_v2_derived_',
    #     '/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/QSO-fnl100/z6_base-A/chain_v3_derived_',
    # ]
    # compare_chain(fn_all, labels=['HODv2, base-A-dv', 'HODv3, base-A'], colors=['red', 'blue'], out='../output/HOD_dv_QSO6.pdf')

