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
    ### QSO6
    fn_all = [
        '/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/QSO-fnl100/z6_base-A/chain_v3_',
        '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl100/z6_base-A/chain_v2.1_',
    ]
    compare_chain(fn_all, labels=['HODv3', 'chain v2.1'], colors=['red', 'blue'], out='../output/HODversion_QSO6.pdf')
    
    ### QSO1
    fn_all = [
        '/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/QSO-fnl100/z1_base-A/chain_v3_',
        '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl100/z1_base-A/chain_v2.1_',
    ]
    compare_chain(fn_all, labels=['HODv3', 'chain v2.1'], colors=['red', 'blue'], out='../output/HODversion_QSO1.pdf')
