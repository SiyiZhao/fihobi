import numpy as np
import matplotlib.pyplot as plt
from getdist import loadMCSamples, plots
import matplotlib as mpl
mpl.rc_file('/global/homes/s/siyizhao/projects/fihobi/fig/matplotlibrc')

import os, sys
sys.path.insert(0, os.path.abspath('../../src'))
from chain_helper import chain


def compare_chain(fn_all, labels=['chain1', 'chain2'], colors=['red', 'blue'], limit_param=False, out='triangle_plot.png'):
    samples_all = []
    params = []
    param_limits = {}
    bestfits = {}
    for fn in fn_all:
        samples = loadMCSamples(fn, settings={'ignore_rows':0.01})
        samples_all.append(samples)
        # Get parameter names and update limits
        if limit_param==True:
            pnames = samples.getParamNames().list()
            for name in pnames:
                if name not in params:
                    params.append(name)
                    bestfits[name] = []
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
    
if __name__ == "__main__":
    def logsigma(params):
        sigma = params[2]
        return np.log10(sigma)
    
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
    
    ### LRG1
    chain_A = chain(outdir='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/LRG-fnl100/z1_base-A/', filename='/chain_v3_')
    chain_A.read_pmn()
    chain_A.derive_new_params(derive_func=logalpha_c, new_para='log_alpha_c', new_para_label='\log \\alpha_c', filename='/chain_v3_derived_')
    chain_A.derive_new_params(derive_func=logalpha_s, new_para='log_alpha_s', new_para_label='\log \\alpha_s', filename='/chain_v3_derived_')
    chain_dv = chain(outdir='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv2/LRG-fnl100/z1_base-A-dv/', filename='/chain_v2_')
    chain_dv.read_pmn()
    chain_dv.derive_new_params(derive_func=unit_alpha_c, new_para='log_alpha_c', new_para_label='\log \\alpha_c', filename='/chain_v2_derived_')
    chain_dv.derive_new_params(derive_func=unit_alpha_s, new_para='log_alpha_s', new_para_label='\log \\alpha_s', filename='/chain_v2_derived_')
    fn_all = [
        '/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv2/LRG-fnl100/z1_base-A-dv/chain_v2_derived_',
        '/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/LRG-fnl100/z1_base-A/chain_v3_derived_',
    ]
    compare_chain(fn_all, labels=['HODv2, base-A-dv', 'HODv3, base-A'], colors=['red', 'blue'], out='../output/HOD_dv_LRG1.pdf')
    
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

