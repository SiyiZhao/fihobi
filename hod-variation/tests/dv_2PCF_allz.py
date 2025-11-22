# python tests/dv_2PCF_allz.py

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')
import yaml
import os, sys
sys.path.insert(0, os.path.abspath('source'))
from data_object import data_object

# clustering to be plotted
z_mock = {'z1': 0.95, 'z2': 1.25, 'z3': 1.55, 'z4': 2.0, 'z5': 2.5, 'z6': 3.0}

def compare_2PCF_dv(tag):
    z = z_mock[tag]
    path_cfg = f'/global/homes/s/siyizhao/projects/fihobi/hod-variation/configs/QSO-fnl100/{tag}_base-dv.yaml'
    path = f'/pscratch/sd/s/siyizhao/data_learnCosm/AbacusMocks/QSO{tag}-fnl100bf/Abacus_pngbase_c302_ph000/z{z:.3f}/galaxies_rsd/clustering.npy'
    path_dv = f'/pscratch/sd/s/siyizhao/data_learnCosm/AbacusMocks/QSO{tag}-fnl100bf/Abacus_pngbase_c302_ph000/z{z:.3f}/galaxies_rsd_dv/clustering.npy'
    clus = np.load(path, allow_pickle=True).item()['QSO_QSO']
    clus_dv = np.load(path_dv, allow_pickle=True).item()['QSO_QSO']

    # observation data
    config_full=yaml.safe_load(open(path_cfg))
    HOD_params = config_full.get("HOD_params", {})
    clustering_params = config_full.get("clustering_params", {})
    data_params = config_full.get("data_params", {})
    data_obj = data_object(data_params, HOD_params, clustering_params)

    # manage data

    # Observations (background only)
    obs_wp  = np.asarray(data_obj.wp['QSO_QSO'])
    obs_xi  = np.asarray(data_obj.xi02['QSO_QSO'])
    obs = {'wp': obs_wp, 'xi0': obs_xi[:,0], 'xi2': obs_xi[:,1]}
    errall_d=np.sqrt(np.diag(data_obj.cov['QSO_QSO']))

    err_obs={}
    the={}
    the_dv={}

    istart=0
    err_obs['wp']=errall_d[istart:istart+len(obs['wp'])]
    the['wp']=clus[istart:istart+len(obs['wp'])]
    the_dv['wp']=clus_dv[istart:istart+len(obs['wp'])]

    istart+=len(obs['wp'])
    err_obs['xi0']=errall_d[istart:istart+len(obs['xi0'])]
    the['xi0']=clus[istart:istart+len(obs['xi0'])]
    the_dv['xi0']=clus_dv[istart:istart+len(obs['xi0'])]

    istart+=len(obs['xi0'])
    err_obs['xi2']=errall_d[istart:istart+len(obs['xi2'])]        
    the['xi2']=clus[istart:istart+len(obs['xi2'])]
    the_dv['xi2']=clus_dv[istart:istart+len(obs['xi2'])]


    # plot

    fig, axs = plt.subplots(2,3,constrained_layout=True,sharex='col',figsize=(24,8),gridspec_kw={'height_ratios': [3, 1]})

    # x-bins and midpoints
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

    # Plot    
    for i,ctype in enumerate(ctypes):
        if ctype=='wp':
            x=rp_wp
        else:
            x=s_xi
        ## obs
        axs[0,i].errorbar(x,x*obs[ctype],yerr=x*err_obs[ctype],marker='o',ls='',color='black',label='loa-v1.1')
        axs[1,i].fill_between(x,(-err_obs[ctype])/obs[ctype],(err_obs[ctype])/obs[ctype],color='lightgray')
        ## models
        axs[0,i].plot(x,x*the_dv[ctype],color='black',label=f'{tag} bestfit, w/ dv')
        axs[1,i].plot(x,(the_dv[ctype]-obs[ctype])/obs[ctype],color='black')
        axs[0,i].plot(x,x*the[ctype],color='red',label='w/o dv')
        axs[1,i].plot(x,(the[ctype]-obs[ctype])/obs[ctype],color='red')
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
    axs[1,2].set_ylim(-0.5,0.5)
    axs[0,0].legend(frameon=False,fontsize=20,loc=4)
    fn_out = f'output/test_{tag}dv.png'
    fig.savefig(fn_out,dpi=300)
    print('Save figure to:', fn_out)
    
if __name__ == "__main__":
    tags = ['z1', 'z2', 'z3', 'z4', 'z6']
    for tag in tags:
        compare_2PCF_dv(tag)
        