# Credit: https://github.com/ahnyu/hod-variation/blob/main/source/post_helpers.py , modified for our use case

import matplotlib.pyplot as plt
import numpy as np

_DEEP_HEX = [
    "#3D5A80", "#C44536","#E0A458","#2A9D8F","#81B29A","#B56576"]
    
def compute_wp(Ball,nthread,out=False):
    mock_dict = Ball.run_hod(tracers=Ball.tracers, want_rsd=Ball.want_rsd, Nthread = nthread, verbose = False, write_to_disk=out)
    clustering = Ball.compute_wp(mock_dict, Ball.rpbins, Ball.pimax, Ball.pi_bin_size, Nthread = nthread)
    
    return mock_dict,clustering



def read_bf_clus(config_full, tracer='QSO'):
    'read the best-fit clustering measured by post.py, input: config file'
    sim_params = config_full['sim_params']
    hod_params = config_full['HOD_params']
    output_dir = sim_params['output_dir']
    sim_name = sim_params['sim_name']
    z_mock = sim_params['z_mock']
    mock_dir = output_dir + sim_name + f'/z{z_mock:.3f}'
    want_rsd = hod_params.get('want_rsd', False)
    want_dv = hod_params.get('want_dv', False)
    if want_rsd:
        rsd_string = '_rsd'
        if want_dv:
            rsd_string += '_dv'
    else:
        rsd_string = ''
    outdir = mock_dir + '/galaxies' + rsd_string
    path2cluster = outdir + f'/{tracer}s_clustering.npy'
    clustering_bf = np.load(path2cluster, allow_pickle=True).item()
    return clustering_bf



def plot_all(data_obj,tracer,clustering,idxwp=np.arange(3,21), idxxi=np.arange(8,21),clustering_other=None,labels=None,colors=None,text=None,out=None):

    fig, axs = plt.subplots(2,3,constrained_layout=True,sharex='col',figsize=(24,8),gridspec_kw={'height_ratios': [3, 1]})
    
    composite_key = f"{tracer}_{tracer}"
    
    # x-bins and midpoints
    rpbins=np.geomspace(0.01,100,25)
    rpbinsmid=(rpbins[1:]+rpbins[:-1])/2
    rp_wp=rpbinsmid[idxwp]
    s_xi=rpbinsmid[idxxi]
    
    ctypes=['wp','xi0','xi2']
    y0labels=[r'$r_{\rm p} w_{\rm p}$',r'$s \xi_{0}$',r'$s \xi_{2}$']
    y1labels=[r'$\Delta w_{\rm p}/w_{\rm p}^{\rm obs}$',r'$\Delta \xi_{0}/\xi_{0}^{\rm obs}$',r'$\Delta \xi_{2}/\xi_{2}^{\rm obs}$']
    xlabels=[r'$r_{\rm p}$',r'$s$',r'$s$']
    
    # Observations (background only)
    obs_wp  = np.asarray(data_obj.wp[composite_key])
    obs_xi  = np.asarray(data_obj.xi02[composite_key])
    obs = {'wp': obs_wp, 'xi0': obs_xi[:,0], 'xi2': obs_xi[:,1]}
    err_obs={}
    the={}
    errall_d=np.sqrt(np.diag(data_obj.cov[composite_key]))
    
    istart=0
    err_obs['wp']=errall_d[istart:istart+len(obs['wp'])]
    the['wp']=clustering[composite_key][istart:istart+len(obs['wp'])]
    
    istart+=len(obs['wp'])
    err_obs['xi0']=errall_d[istart:istart+len(obs['xi0'])]
    the['xi0']=clustering[composite_key][istart:istart+len(obs['xi0'])]
    
    istart+=len(obs['xi0'])
    err_obs['xi2']=errall_d[istart:istart+len(obs['xi2'])]        
    the['xi2']=clustering[composite_key][istart:istart+len(obs['xi2'])]
    
    # Slice other
    if clustering_other is not None:
        the_others = []
        for vec in clustering_other:
            d, istart = {}, 0
            d['wp']  = vec[composite_key][istart:istart+len(obs['wp'])];  istart += len(obs['wp'])
            d['xi0'] = vec[composite_key][istart:istart+len(obs['xi0'])]; istart += len(obs['xi0'])
            d['xi2'] = vec[composite_key][istart:istart+len(obs['xi2'])]
            the_others.append(d)
        if labels is None:
            labels = [f"Model {i+1}" for i in range(len(the_others))]
        if colors is None:
            colors = _DEEP_HEX
    
    # Plot    
    for i,ctype in enumerate(ctypes):
        if ctype=='wp':
            x=rp_wp
        else:
            x=s_xi
        axs[0,i].errorbar(x,x*obs[ctype],yerr=x*err_obs[ctype],marker='o',ls='',color='black',label='loa-v1.1')
        label_the='Best fit' if labels is None else labels[0]
        axs[0,i].plot(x,x*the[ctype],color='black',label=label_the)
        axs[1,i].plot(x,(the[ctype]-obs[ctype])/obs[ctype],color='black')
        axs[1,i].fill_between(x,(-err_obs[ctype])/obs[ctype],(err_obs[ctype])/obs[ctype],color='lightgray')
        if clustering_other is not None:
            for j,d in enumerate(the_others):
                axs[0,i].plot(x,x*d[ctype],lw=1.5,color=colors[(j+1)%len(colors)],label=labels[j+1] if i==1 else None)
                axs[1,i].plot(x,(d[ctype]-obs[ctype])/obs[ctype],lw=1.5,color=colors[(j+1)%len(colors)])
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
    axs[0,1].legend(frameon=False,fontsize=20,loc=3)
    if text is not None:
        axs[0,0].annotate(text,xy=(0.05,0.85),xycoords='axes fraction',fontsize=20)
    if out is not None:
        fig.savefig(out,dpi=360,bbox_inches='tight',facecolor='white', transparent=False)
    plt.show()


def plot_all_compare(
    data_obj,
    tracer,
    clustering_baseline,
    clustering_others,
    labels=None,
    color=None,
    idxwp=np.arange(3,21),
    idxxi=np.arange(8,21),
    text=None,
    out=None
):
    fig, axs = plt.subplots(
        2, 3, constrained_layout=True, sharex='col',
        figsize=(24, 8), gridspec_kw={'height_ratios': [3, 1]}
    )

    composite_key = f"{tracer}_{tracer}"

    # x-bins and midpoints
    rpbins = np.geomspace(0.01, 100, 25)
    rpbinsmid = (rpbins[1:] + rpbins[:-1]) / 2.0
    rp_wp = rpbinsmid[idxwp]
    s_xi  = rpbinsmid[idxxi]

    ctypes   = ['wp','xi0','xi2']
    y0labels = [r'$r_{\rm p} w_{\rm p}$', r'$s \,\xi_{0}$', r'$s \,\xi_{2}$']
    y1labels = [r'$w_{\rm p}/w_{\rm p}^{\rm base}$',
                r'$\xi_{0}/\xi_{0}^{\rm base}$',
                r'$\xi_{2}/\xi_{2}^{\rm base}$']
    xlabels  = [r'$r_{\rm p}$', r'$s$', r'$s$']

    # Observations (background only)
    obs_wp  = np.asarray(data_obj.wp[composite_key])
    obs_xi  = np.asarray(data_obj.xi02[composite_key])
    obs = {'wp': obs_wp, 'xi0': obs_xi[:,0], 'xi2': obs_xi[:,1]}

    # Flatten baseline/others no matter how they are passed in
    base_vec = clustering_baseline[composite_key]
    other_vecs = [m[composite_key] for m in clustering_others]

    # Slice baseline into components
    the_base, istart = {}, 0
    the_base['wp']  = base_vec[istart:istart+len(obs['wp'])];  istart += len(obs['wp'])
    the_base['xi0'] = base_vec[istart:istart+len(obs['xi0'])]; istart += len(obs['xi0'])
    the_base['xi2'] = base_vec[istart:istart+len(obs['xi2'])]

    # Slice others
    the_others = []
    for vec in other_vecs:
        d, istart = {}, 0
        d['wp']  = vec[istart:istart+len(obs['wp'])];  istart += len(obs['wp'])
        d['xi0'] = vec[istart:istart+len(obs['xi0'])]; istart += len(obs['xi0'])
        d['xi2'] = vec[istart:istart+len(obs['xi2'])]
        the_others.append(d)

    # Labels
    if labels is None:
        labels = [f"Model {i+1}" for i in range(len(the_others))]
    if color is None:
        color = _DEEP_HEX

    for i, ctype in enumerate(ctypes):
        x = rp_wp if ctype == 'wp' else s_xi

        # --- Top: absolute x*stat ---
        # Obs background as faint points
        axs[0, i].plot(x, x*obs[ctype], marker='o', ls='', ms=4, color='0.85', alpha=0.8)

        # Baseline in gray
        axs[0, i].plot(x, x*the_base[ctype], color='0.5', lw=2.5, label='Baseline' if i==0 else None)

        # Others in color
        for j, d in enumerate(the_others):
            axs[0, i].plot(x, x*d[ctype], lw=2.2, color=color[j % len(color)],
                           label=labels[j] if i==0 else None)

        # --- Bottom: ratio to baseline ---
        axs[1, i].axhline(1.0, ls='-.', color='0.5', lw=1.5)
        base = the_base[ctype]
        denom = np.where(base != 0.0, base, np.nan)
        for j, d in enumerate(the_others):
            axs[1, i].plot(x, d[ctype]/denom, lw=2.0, color=color[j % len(color)])

        # Cosmetics
        axs[0, i].set_xscale('log'); axs[1, i].set_xscale('log')
        axs[0, i].set_ylabel(y0labels[i], fontsize=20)
        axs[1, i].set_ylabel(y1labels[i], fontsize=20)
        axs[1, i].set_xlabel(xlabels[i], fontsize=20)
        axs[0, i].grid(ls='--', alpha=0.4); axs[1, i].grid(ls='--', alpha=0.4)
        axs[0, i].tick_params(labelsize=20); axs[1, i].tick_params(labelsize=20)

    # Ratio limits
    for i in range(3):
        axs[1, i].set_ylim(0.5, 1.5)

    if len(the_others):
        axs[0, 0].legend(frameon=False, fontsize=18, loc=0)

    if text is not None:
        axs[0, 0].annotate(text, xy=(0.05, 0.85), xycoords='axes fraction', fontsize=20)

    if out is not None:
        fig.savefig(out, dpi=360, bbox_inches='tight', facecolor='white', transparent=False)
    plt.show()


def plot_all_realizations(data_obj,tracer,wpall,xi0all,xi2all,text=None,out=None):

    fig, axs = plt.subplots(2,3,constrained_layout=True,sharex='col',figsize=(24,8),gridspec_kw={'height_ratios': [3, 1]})
    
    composite_key = f"{tracer}_{tracer}"
    
    rpbins=np.geomspace(0.01,100,25)
    rpbinsmid=(rpbins[1:]+rpbins[:-1])/2
    idxwp=np.arange(3,21)
    idxxi=np.arange(8,21)
    rp_wp=rpbinsmid[idxwp]
    s_xi=rpbinsmid[idxxi]
    
    ctypes=['wp','xi0','xi2']
    y0labels=[r'$r_{\rm p} w_{\rm p}$',r'$s \xi_{0}$',r'$s \xi_{2}$']
    y1labels=[r'$\Delta w_{\rm p}/w_{\rm p}^{\rm obs}$',r'$\Delta \xi_{0}/\xi_{0}^{\rm obs}$',r'$\Delta \xi_{2}/\xi_{2}^{\rm obs}$']
    xlabels=[r'$r_{\rm p}$',r'$s$',r'$s$']
    
    obs={}
    obs['wp']=data_obj.wp[composite_key]
    obs['xi0']=data_obj.xi02[composite_key][:,0]
    obs['xi2']=data_obj.xi02[composite_key][:,1]
    err_obs={}
    the={}
    errall_d=np.sqrt(np.diag(data_obj.cov[composite_key]))
    
    istart=0
    err_obs['wp']=errall_d[istart:istart+len(obs['wp'])]
    the['wp']=wpall[:,0]
    
    istart+=len(obs['wp'])
    err_obs['xi0']=errall_d[istart:istart+len(obs['xi0'])]
    the['xi0']=xi0all[:,0]
    
    istart+=len(obs['xi0'])
    err_obs['xi2']=errall_d[istart:istart+len(obs['xi2'])]        
    the['xi2']=xi2all[:,0]
        
    for i,ctype in enumerate(ctypes):
        if ctype=='wp':
            x=rp_wp
        else:
            x=s_xi
        axs[0,i].errorbar(x,x*obs[ctype],yerr=x*err_obs[ctype],marker='o',ls='',color='black',label='loa-v1.1-pip')
        axs[0,i].plot(x,x*the[ctype],zorder=5,color='black',label='ph000 best fit')
        for j in range(24):            
            if ctype=='wp': 
                axs[0,i].plot(x,x*wpall[:,j+1],color='lightgray')
            elif ctype=='xi0':
                axs[0,i].plot(x,x*xi0all[:,j+1],color='lightgray')
            elif ctype=='xi2':
                axs[0,i].plot(x,x*xi2all[:,j+1],color='lightgray')        
        axs[1,i].plot(x,(the[ctype]-obs[ctype])/obs[ctype],color='black')
        axs[1,i].fill_between(x,(-err_obs[ctype])/obs[ctype],(err_obs[ctype])/obs[ctype],color='lightgray')
        
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
    
    axs[0,0].legend(frameon=False,fontsize=20,loc=4)
    if text is not None:
        axs[0,0].annotate(text,xy=(0.05,0.85),xycoords='axes fraction',fontsize=20)
    if out is not None:
        fig.savefig(out,dpi=360,bbox_inches='tight',facecolor='white', transparent=False)
    plt.show()
    

