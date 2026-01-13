import numpy as np
import matplotlib.pyplot as plt
from getdist import loadMCSamples, plots
import matplotlib as mpl
mpl.rc_file('/global/homes/s/siyizhao/projects/fihobi/fig/matplotlibrc')

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
    parent_dir = '/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/'
    ### LRGs
    fn_all = [
        parent_dir + 'LRG-fnl100/z1_base-A/chain_v3_',
        parent_dir + 'LRG-fnl100/z2_base-A/chain_v3_',
        parent_dir + 'LRG-fnl100/z3_base-A/chain_v3_',
    ]
    compare_chain(fn_all, labels=['LRG z0p500', 'LRG z0p725', 'LRG z0p950'], colors=['red', 'blue', 'green'], out='../output/HODv3_LRGs.pdf')
    
    ### low-z QSOs
    fn_all = [
        parent_dir + 'QSO-fnl100/z1_base-A/chain_v3_',
        parent_dir + 'QSO-fnl100/z2_base-A/chain_v3_',
        parent_dir + 'QSO-fnl100/z3_base-A/chain_v3_',
    ]
    compare_chain(fn_all, labels=['QSO z0p950', 'QSO z1p250', 'QSO z1p550'], colors=['red', 'blue', 'green'], out='../output/HODv3_lowzQSOs.pdf', limit_param=True)
    
    ### high-z QSOs
    fn_all = [
        parent_dir + 'QSO-fnl100/z4_base-A/chain_v3_',
        parent_dir + 'QSO-fnl100/z5_base-A/chain_v3_',
        parent_dir + 'QSO-fnl100/z6_base-A/chain_v3_',
    ]
    compare_chain(fn_all, labels=['QSO z2p000', 'QSO z2p500', 'QSO z3p000'], colors=['red', 'blue', 'green'], out='../output/HODv3_highzQSOs.pdf', limit_param=True)
    