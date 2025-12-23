# python plot_sample_2PCF.py --cfgs4HIP test/QSO_2.8_3.5/config.yaml
import argparse
import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')
import os, sys
sys.path.insert(0, '../src')
from io_def import path_to_clustering, load_config, path_to_HODconfigs


colors = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]
idxwp=np.arange(6,21)
idxxi=np.arange(11,21)
rpbins=np.geomspace(0.01,100,25)
rpbinsmid=(rpbins[1:]+rpbins[:-1])/2
rp_wp=rpbinsmid[idxwp]
s_xi=rpbinsmid[idxxi]

ctypes=['wp','xi0','xi2']
y0labels=[r'$r_{\rm p} w_{\rm p}$',r'$s \xi_{0}$',r'$s \xi_{2}$']
y1labels=[r'$\Delta w_{\rm p}/w_{\rm p}^{\rm obs}$',r'$\Delta \xi_{0}/\xi_{0}^{\rm obs}$',r'$\Delta \xi_{2}/\xi_{2}^{\rm obs}$']
xlabels=[r'$r_{\rm p}$',r'$s$',r'$s$']

def load_data(tracer, zmin, zmax, version='v1.1'):
    ddir=f'../data/for_hod/{version}_rp6s11/'
    path=ddir+f'wp_{tracer}_{zmin}_{zmax}_cut.dat'
    data=np.loadtxt(path)
    wp=data[:,1]
    wp_err=data[:,2]
    path=ddir+f'xi02_{tracer}_{zmin}_{zmax}_cut.dat'
    data=np.loadtxt(path)
    xi0=data[:,1]
    xi0err=data[:,2]
    xi2=data[:,3]
    xi2err=data[:,4]
    obs={'wp':wp,'xi0':xi0,'xi2':xi2}
    err={'wp':wp_err,'xi0':xi0err,'xi2':xi2err}
    return obs, err

def read_mock_clus(path, len_wp=15, len_xi0=10, len_xi2=10):
    data = np.load(path, allow_pickle=True)#.item()
    # dvec = data['QSO_QSO']
    dvec = data
    if len_wp+len_xi0+len_xi2 != dvec.shape[0]:
        print(f"Length mismatch: expected {len_wp+len_xi0+len_xi2}, got {dvec.shape[0]}")
    the = {'wp': dvec[0:len_wp], 'xi0': dvec[len_wp:len_wp+len_xi0], 'xi2': dvec[len_wp+len_xi0:len_wp+len_xi0+len_xi2]}
    return the

def load_theory(config, num=None, want_MAP=False, len_wp=15, len_xi0=10, len_xi2=10):
    sim_params = load_config(config).get("sim_params", {})
    if want_MAP:
        path = path_to_clustering(sim_params, tracer=tracer, prefix='MAP')
        # mock_dir = path_to_mock_dir(config)
        # path = os.path.join(mock_dir, 'QSOs_clustering.npy')
        the = read_mock_clus(path, len_wp, len_xi0, len_xi2)
        return the
    elif num is not None:
        cmap = plt.get_cmap('viridis')
        the_all = []
        the_colors = []
        the_labels = []
        for i in range(num):
            path = path_to_clustering(sim_params, tracer=tracer, prefix=f'r{i}')
            the = read_mock_clus(path, len_wp, len_xi0, len_xi2)
            the_all.append(the) 
            color = cmap(i / num)
            the_colors.append(color)
            the_labels.append(f'r{i}')
        return the_all, the_colors, the_labels
    else:
        raise ValueError("Either num or want_MAP must be specified.")

if __name__ == "__main__":
    ## load config
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfgs4HIP', type=str, default='HIP.yaml', help='Path to the HIP config file, do not provide --config.')
    args = parser.parse_args()
    cfgs4HIP = args.cfgs4HIP
    cfgs_HIP = load_config(cfgs4HIP)
    cfgs_sample = cfgs_HIP.get('sampleHOD', {})
    cfgs_galaxy = cfgs_HIP.get('galaxy', {})
    tracer = cfgs_galaxy.get('tracer', 'QSO')
    zmin = cfgs_galaxy.get('zmin', 2.8)
    zmax = cfgs_galaxy.get('zmax', 3.5)
    # config = path_to_HODconfigs(cfgs4HIP)
    path2cfgHOD = cfgs_HIP['HODfit']['path2cfgHOD']
    # tracer, zmin, zmax = 'QSO', 2.8, 3.5
    # config = 'configs/QSO-fnl100/z6_base.yaml'

    ## Load data
    obs_v1, err_v1 = load_data(tracer, zmin, zmax, version='v1.1')
    obs_v2, err_v2 = load_data(tracer, zmin, zmax, version='v2')

    obs_all = [obs_v1, obs_v2]
    err_all = [err_v1, err_v2]
    labels = ['loa-v1.1', 'loa-v2']

    ## Load theory
    len_wp = obs_v2['wp'].shape[0]
    len_xi0 = obs_v2['xi0'].shape[0]
    len_xi2 = obs_v2['xi2'].shape[0]
    the_all, the_colors, the_labels = load_theory(path2cfgHOD, num=10)
    the_map = load_theory(path2cfgHOD, want_MAP=True)

    ## Plotting
    fig, axs = plt.subplots(2,3,constrained_layout=True,sharex='col',figsize=(24,8),gridspec_kw={'height_ratios': [3, 1]})
    for i,ctype in enumerate(ctypes):
        if ctype=='wp':
            x=rp_wp
        else:
            x=s_xi
        for obs, err, color, label in zip(obs_all, err_all, colors, labels):
            axs[0,i].errorbar(x, x*obs[ctype], yerr=x*err[ctype], 
                        marker='o', ls='', markerfacecolor='none',
                        markeredgecolor=color, ecolor=color,
                        label=label)
            # make the band hollow: no face fill, only an outline
            axs[1,i].fill_between(x, (-err[ctype]) / obs[ctype], (err[ctype]) / obs[ctype],
                facecolor='none', edgecolor=color, linewidth=1.5, alpha=1.0)
        axs[0,i].plot(x, x*the_map[ctype], ls='-', color='black', label='MAP of HOD')
        axs[1,i].plot(x, (the_map[ctype]-obs_v2[ctype])/obs_v2[ctype], ls='-', color='black')
        for the, color, label in zip(the_all, the_colors, the_labels):
            axs[0,i].plot(x, x*the[ctype], ls='-', color=color, label=label, alpha=0.5)
            fractional_error = (the[ctype] - obs_v2[ctype]) / obs_v2[ctype]
            axs[1,i].plot(x, fractional_error, ls='-', color=color, alpha=0.5)
        axs[0,i].set_xscale('log')
        axs[1,i].set_xscale('log')
        axs[0,i].set_ylabel(y0labels[i],fontsize=20)
        axs[1,i].set_ylabel(y1labels[i],fontsize=20)
        axs[0,i].grid(linestyle='--')
        axs[1,i].grid(linestyle='--')        
        axs[0,i].tick_params(labelsize=20)
        axs[1,i].tick_params(labelsize=20)        
        axs[1,i].set_xlabel(xlabels[i],fontsize=20)
        axs[1,i].plot(x,np.zeros_like(x),ls='-.',color='black')    
    # axs[1,1].set_ylim(-0.5,0.5)
    if max(abs(err_v1['xi2']/obs_v1['xi2']))>1 or max(abs(err_v2['xi2']/obs_v2['xi2']))>1:
        axs[1,2].set_ylim(-1,1)
    axs[0,0].legend(frameon=False,fontsize=20,loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=2)
    fout="sampleHOD_plot.png"
    plt.savefig(fout)
    print(f"[plot] -> {fout}")