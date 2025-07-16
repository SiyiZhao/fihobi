#!/usr/bin/env python3
'''
Plotting results from Dynesty runs using its plotting tools and GetDist.
'''

import numpy as np
import matplotlib.pyplot as plt
from dynesty import plotting as dyplot
from getdist import MCSamples, plots

# ## input
# path_chain = '../data/l/HOD_fit_y3/dynesty/nest_results.npz'
# ## output
# path_info = 'output/y3.txt'
# path_plot_run = 'plot/y3_run.png'
# path_plot_trace = 'plot/y3_trace.png'
# path_plot_corner = 'plot/y3_corner.png'
# path_plot_getdist = 'plot/y3_getdist.png'

## input
path_chain = '../data/l/HOD_fit_yuan/dynesty/test_results.npz'
## output
path_info = 'output/sv3.txt'
path_plot_run = 'plot/sv3_run.png'
path_plot_trace = 'plot/sv3_trace.png'
path_plot_corner = 'plot/sv3_corner.png'
path_plot_getdist = 'plot/sv3_getdist.png'


ndim = 5
names = ["logM_cut", "logM1", "sigma", "alpha", "kappa"]
labels = [r"$\log M_{\text{cut}}$", r"$\log M_1$", r"$\sigma$", r"$\alpha$", r"$\kappa$"]

truths = [12.78,13.94,0.17,1.07,0.55] # yuan's results

## load & print results
data = np.load(path_chain, allow_pickle=True)
arr = data['res']
res = arr.item()

# with open(path_info, 'w') as f:
#     print(res.summary(), file=f)
# print(res.summary())
res.summary()  # print summary to console
    
## plot run
lnz_truth = ndim * -np.log(2 * 10.)  # analytic evidence solution
fig, axes = dyplot.runplot(res, lnz_truth=lnz_truth)  # summary (run) plot
plt.savefig(path_plot_run, dpi=300, bbox_inches='tight')
plt.clf()
## trace
fig, axes = dyplot.traceplot(res, truths=truths, labels=labels, truth_color='black', show_titles=True, trace_cmap='viridis', connect=True, connect_highlight=range(5))
plt.savefig(path_plot_trace, dpi=300, bbox_inches='tight')
plt.clf()
## corner plot
fig, ax = dyplot.cornerplot(res, color='blue', truths=truths, labels=labels, truth_color='black', show_titles=True,max_n_ticks=3, quantiles=None)
plt.savefig(path_plot_corner, dpi=300, bbox_inches='tight')
plt.clf()



## getdist

samples, weights = res.samples, res.importance_weights()
labels = [r"\log M_{\text{cut}}", r"\log M_1", r"\sigma", r"\alpha", r"\kappa"]

gdsamples = MCSamples(samples=samples, weights=weights, names=names, labels=labels)

g = plots.get_subplot_plotter()
g.triangle_plot(gdsamples, filled=True, title_limit=1)
# g.triangle_plot(gdsamples, truths=truths, filled=True, title_limit=1)
plt.savefig(path_plot_getdist, dpi=300, bbox_inches='tight')
plt.clf()
