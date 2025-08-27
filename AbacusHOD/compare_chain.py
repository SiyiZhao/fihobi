from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')

gds_000 = loadMCSamples('../data/l/HODfit_test_z0/pmn/test')
gds_fnl30 = loadMCSamples('../data/l/HODfit_test_z0_fnl30/pmn/test')

g = plots.get_subplot_plotter()
g.triangle_plot([gds_000, gds_fnl30], legend_labels=['c000', 'c300, fnl=30'], filled=False, contour_colors=['C0', 'C1'], )

plt.savefig('plot/compare_chain_fnl30.png', dpi=300, bbox_inches='tight')