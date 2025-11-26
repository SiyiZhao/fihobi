# -*- coding: utf-8 -*-
"""
Workspace: projects/fihobi/inference/
"""

import yaml
import os
import numpy as np
from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')

class chain:
    '''
    Derive new parameters of the chain, and plot them together.
    '''
    def __init__(self, outdir, filename='/_', param_name=None, param_label=None):
        '''
        outdir, filename: output directory & filename.
        
        Can leave None, and then read from .paramnames file:
        param_name: list of param names. 
        param_label: LaTeX labels of param names.
        '''
        self.outdir = outdir
        self.filename = filename
        self.param_name = param_name
        self.param_label = param_label
        
        if not os.path.exists(self.outdir):
            raise FileNotFoundError(f"The dir {self.outdir} does not exist, please prepare the chain first!")

    def read_pmn(self):
        '''
        read the chain from pymultinest.
        
        [root].txt: weight like param1 param2 param3 ...
        [root].paramnames: param label, e.g. logMq \\log M_q (param and label must be separated by the first space)
        '''
        pmn_chain = self.outdir + self.filename + ".txt"
        self.chain = np.loadtxt(pmn_chain)
        ## read .paramnames file
        pmn_par = self.outdir + self.filename + ".paramnames"
        name = []
        label = []
        with open(pmn_par, 'r') as f:
            for line in f:
                parts = line.split(" ",1)
                if len(parts) == 2:
                    name.append(parts[0])
                    label.append(parts[1].strip())
                else:
                    print("Line format error: ", line)  
        self.param_name = name
        self.param_label = label
                
    def best_fit(self):
        '''
        return the best fit parameters.
        '''
        best_fit = self.chain[np.argmax(self.chain[:,0])]
        return best_fit
    
    def derive_new_params(self, derive_func, new_para, new_para_label=None, filename='derived_'):
        '''
        derive a new parameter from the chain.
        write the new chain to a new file.
        also write a new .paramnames file.
        new_para: str, new parameter name.
        '''
        params_chain = self.chain[:, 2:]
        new_param_chain = []
        for params in params_chain:
            new_param = derive_func(params)
            new_param_chain.append(new_param)
        new_chain = np.hstack((self.chain, np.array(new_param_chain).reshape(-1,1)))
        self.chain = new_chain
        self.filename = filename
        ## write .txt file
        np.savetxt(self.outdir + filename + ".txt", new_chain)
        print(f"new chain written.")
        ## write .paramnames file
        if new_para_label is None:
            new_para_label = new_para
        self.param_name.append(new_para+'*') # mark the derived parameters as GetDist convention
        self.param_label.append(new_para_label)
        pmn_par = self.outdir + self.filename + ".paramnames"
        with open(pmn_par, 'w') as f:
            for name, label in zip(self.param_name, self.param_label):
                f.write(f"{name} {label}\n")
        print(f"new param names written.")
        
    def plot_result(self, plot_path=None):
        'plot the result.'
        samples = loadMCSamples(self.outdir+self.filename, settings={'ignore_rows':0.01})     
        if plot_path is None:
            plot_path = self.outdir+'plot.png'
        g = plots.get_subplot_plotter()
        g.triangle_plot(samples, filled=True, title_limit=1)
        plt.savefig(plot_path)
        print(f"plot saved to {plot_path}")
        plt.close()



def load_chain_prefix(fn):
    # Load YAML configuration.
    with open(fn, 'r') as f:
        config = yaml.safe_load(f) 
    chain_params = config['chain_params']
    chain_prefix = chain_params['chain_prefix']
    output_dir = chain_params['output_dir']
    return output_dir+chain_prefix
    

def compare_chain(fn_all, labels=['chain1', 'chain2'], colors=['red', 'blue'], markers={'p':1.0}, fn_out=None):
    samples_all = []
    for fn in fn_all:
        samples = loadMCSamples(fn, settings={'ignore_rows':0.01})
        samples_all.append(samples)
    
    g = plots.get_subplot_plotter()
    g.settings.legend_fontsize = 30
    g.settings.axes_labelsize = 30
    g.settings.axes_fontsize = 20
    g.settings.linewidth_contour = 2.0   # 改 contour 线条宽度
    g.settings.linewidth = 2.0           # 改 1D 曲线的线宽
    g.triangle_plot(samples_all, params=['p', 'b1', 'sn0', 'sigmas'], markers=markers, legend_labels=labels, legend_loc='upper right', filled=False, contour_colors=colors)
    if fn_out:
        plt.savefig(fn_out, bbox_inches='tight')
        print(f"Saved figure to {fn_out}")
    else:
        plt.show()
        
def compare_chain_bphi(fn_all, labels=['chain1', 'chain2'], colors=['red', 'blue'], fn_out=None):
    samples_all = []
    for fn in fn_all:
        samples = loadMCSamples(fn, settings={'ignore_rows':0.01})
        samples_all.append(samples)
    
    g = plots.get_subplot_plotter()
    g.settings.legend_fontsize = 30
    g.settings.axes_labelsize = 30
    g.settings.axes_fontsize = 20
    g.settings.linewidth_contour = 2.0   # 改 contour 线条宽度
    g.settings.linewidth = 2.0           # 改 1D 曲线的线宽
    g.triangle_plot(samples_all, params=['bphi', 'b1', 'sn0', 'sigmas'], legend_labels=labels, legend_loc='upper right', filled=False, contour_colors=colors)
    if fn_out:
        plt.savefig(fn_out, bbox_inches='tight')
        print(f"Saved figure to {fn_out}")
    else:
        plt.show()
        
def compare_chain_pbphi(fn_all, labels=['chain1', 'chain2'], colors=['red', 'blue'], fn_out=None):
    samples_all = []
    for fn in fn_all:
        samples = loadMCSamples(fn, settings={'ignore_rows':0.01})
        samples_all.append(samples)
    
    g = plots.get_subplot_plotter()
    g.settings.legend_fontsize = 30
    g.settings.axes_labelsize = 30
    g.settings.axes_fontsize = 20
    g.settings.linewidth_contour = 2.0   # 改 contour 线条宽度
    g.settings.linewidth = 2.0           # 改 1D 曲线的线宽
    g.triangle_plot(samples_all, params=['p', 'bphi', 'b1', 'sn0', 'sigmas'], legend_labels=labels, legend_loc='upper right', filled=False, contour_colors=colors)
    if fn_out:
        plt.savefig(fn_out, bbox_inches='tight')
        print(f"Saved figure to {fn_out}")
    else:
        plt.show()
        
