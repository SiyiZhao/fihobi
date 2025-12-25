import numpy as np
import pandas as pd
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from getdist import loadMCSamples, MCSamples, plots
from matplotlib import pyplot as plt
from io_def import (
    ensure_dir,
    load_config, 
    write_config,
    plot_style,
    def_OBSample,
    write_script_to_file,
    path_to_ObsClus,
    path_to_AbacusSubsample,
    path_to_HODchain,
    path_to_mocks,
    write_catalogs,
    path_to_catalog,
    path_to_clustering,
    path_to_poles,
    path_to_hip,
)    

THIS_REPO = Path(__file__).parent.parent
plot_style()

class HIPanOBSample:
    """
    HOD-informed Prior for an Observational Sample.
    """
    def __init__(
        self, 
        cfg_file: str | None = None,
        tracer: str | None = None, 
        zmin: float | None = None, 
        zmax: float | None = None,
        work_dir: Path | None = None,
    ) -> None:
        """
        Either provide a configuration file or specify tracer, zmin, and zmax directly.
        """
        ## define
        self.OBSample = None
        self.work_dir = None
        self.cfg = None
        self.ObsClus = None
        self.HODfit = None
        self.cfgHOD = None # store the loaded cfgHOD to avoid repeated loading
        self.HIP = None
        if cfg_file is not None:
            self.load_cfg(cfg_file)
        else:
            ## check tracer validity
            if tracer not in ['QSO', 'LRG']:
                raise ValueError("tracer must be 'QSO' or 'LRG'")

            self.OBSample = def_OBSample(tracer, zmin, zmax)
            if work_dir is None:
                work_dir = Path(f'./{self.OBSample["tag"]}')
            self.work_dir = work_dir
            self.cfg = {'OBSample': self.OBSample, 'work_dir': str(self.work_dir)}
    
    def load_cfg(self, path: Path) -> None:
        self.cfg = load_config(path)
        print(f"[load] configuration from {path}\n")
        self.OBSample = self.cfg['OBSample']
        self.work_dir = Path(self.cfg['work_dir'])
        self.ObsClus = self.cfg.get('ObsClus', None)
        self.HODfit = self.cfg.get('HODfit', None)
        self.HIP = self.cfg.get('HIP', None)
        ## load cfgHOD if exists
        path2cfgHOD = self.HODfit.get('path2cfgHOD', None) if self.HODfit is not None else None
        if path2cfgHOD is not None:
            self.cfgHOD = load_config(path2cfgHOD)
    
    def save_cfg(self, path: Path=None) -> None:
        if path is None:
            path = self.work_dir / "config.yaml"
        write_config(self.cfg, path)
    
    ##### ----- observed 2PCF ----- #####
    def measure_clustering(
        self,
        verspec: str='loa-v1',
        version: str='v2',
        weight_type: str='pip_angular_bitwise',
        path_script: str=None
    ) -> None:
        from clustering import script_clustering

        tracer = self.OBSample['tracer']
        zmin = self.OBSample['zmin']
        zmax = self.OBSample['zmax']
        tag = self.OBSample['tag']
        path2ObsClus = path_to_ObsClus(verspec=verspec, version=version)
        script = script_clustering(tracer, zmin, zmax, path2ObsClus, sample_name=tag, weight_type=weight_type)   
        if path_script is None:
            path_script = self.work_dir / f"scripts/clustering_{tag}.sh"
        write_script_to_file(script, path_script)
        print("[guide] >>> Go run the script, it will take several hours.\n")
        ## refresh info
        self.ObsClus = {'verspec': verspec, 'version': version, 'weight_type': weight_type, 'path_script': str(path_script), 'path2ObsClus': str(path2ObsClus)}
        self.cfg['ObsClus'] = self.ObsClus
        

    ##### ----- HOD fitting ----- #####    
    def prepare_HOD_fitting(
        self,
        data_dir: Path | None = None,
        data_HOD_dir: Path | None = None,
        cat_dir: Path | None = None,
    ) -> None:
        """
        Prepare data for HOD fitting.
        """
        from HOD_prepare import save_data_for_HODfitting, show_zeff, load_nz
        
        tracer = self.OBSample['tracer']
        zmin = self.OBSample['zmin']
        zmax = self.OBSample['zmax']
        verspec = self.ObsClus['verspec']
        version = self.ObsClus['version']
        ## save clustering data: wp, xi02, cov
        if data_dir is None:
            data_dir = Path(self.ObsClus['path2ObsClus']) 
        y3rppidir = data_dir / "rppi"
        y3smudir = data_dir / "smu"
        if data_HOD_dir is None:
            data_HOD_dir = path_to_ObsClus(verspec=verspec, version=version, mode='forHOD')
        ensure_dir(data_HOD_dir)
        path2data = save_data_for_HODfitting(outdir=data_HOD_dir, y3rppidir=y3rppidir, y3smudir=y3smudir, tracer=tracer, zmin=zmin, zmax=zmax)
        ## print zmin, zmax, zeff of the z-bins 
        if cat_dir is None:
            cat_dir = Path(f'/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/{verspec}/LSScats/{version}/PIP/')
            print(f"Using default catalog directory: {cat_dir}")
        zeff = show_zeff(tracer=tracer, zmin=zmin, zmax=zmax, catdir=cat_dir) 
        ## load n(z) of the z-bins
        nz = load_nz(tracer=tracer, zmin=zmin, zmax=zmax, nzdir=cat_dir)
        print('nbar:', nz)
        ## refresh info
        self.HODfit = {'path2data4HOD': path2data}
        self.OBSample['zeff'] = zeff
        self.OBSample['nbar'] = nz
        self.cfg['HODfit'] = self.HODfit
        
    
    def _hod_latex_labels(self, prior: dict[str, tuple[int, float, float, str]]) -> list[str]:

        labels = []
        latex_map = {
            'logM_cut': {'flat': "\log M_{\\mathrm{cut}}"},
            'logM1': {'flat': "\log M_1"},
            'sigma': {'flat': "\sigma", 'log': "\log \sigma"},
            'alpha': {'flat': "\\alpha", 'log': "\log \\alpha"},
            'kappa': {'flat': "\\kappa", 'log': "\log \\kappa"},
            'alpha_c': {'flat': "\\alpha_{\\mathrm{c}}", 'log': "\log \\alpha_{\\mathrm{c}}"},
            'alpha_s': {'flat': "\\alpha_{\\mathrm{s}}", 'log': "\log \\alpha_{\\mathrm{s}}"},
            'Acent': {'flat': "A_{\\mathrm{cent}}", 'log': "\log A_{\\mathrm{cent}}"},
            'Asat': {'flat': "A_{\\mathrm{sat}}", 'log': "\log A_{\\mathrm{sat}}"},
        }
        for p in prior:
            labels.append(latex_map[p][prior[p][3]])
        
        return labels
    
    def config_HOD_fitting(
        self,
        prior: dict[str, tuple[int, float, float, str]],
        chain_path: Path | None = None,
        version: str='v1',
        mock_dir: Path | None = None,
        sim_name: str="Abacus_pngbase_c302_ph000",
        subsample_dir: Path | None = None,
    ) -> None: 
        """
        Generate and write the configuration file for HOD fitting.
        
        prior: dict of prior settings for each parameter, e.g., {'logM_cut': (0, 12.0, 14.0, 'flat'), 'logM1': (1, 13.0, 15.0, 'flat'), 'sigma': (2, 0.1, 1.0, 'log')}. If the string is 'log', it means log-uniform prior, and the low and high values are in log10 space.
        """
        from abacus_helper import find_zsnap, set_sim_params, set_HOD_tracer, set_HOD_params, set_clustering_params  
        
        tracer = self.OBSample['tracer']
        clus_ver = self.ObsClus['version']
        ## determine zsnap
        zsnap = find_zsnap(self.OBSample['zeff']) 
        print(f"[set] zsnap = {zsnap}")
        ## generate config file
        if mock_dir is None:
            mock_dir = path_to_mocks(self.work_dir)
        if subsample_dir is None:
            subsample_dir = path_to_AbacusSubsample()
        sim_params = set_sim_params(sim_name=sim_name, z_mock=zsnap, output_dir=mock_dir, subsample_dir=subsample_dir)
        hod_QSO = set_HOD_tracer(logM_cut=13.0, logM1=14.0, sigma=0.5, alpha=1.0, kappa=0.0) # the default values are useless
        tracers = {'QSO': hod_QSO}
        HOD_params = set_HOD_params(tracers)
        clustering_params = set_clustering_params()
        data_params = {
            'tracer_combos': {f'{tracer}_{tracer}': self.HODfit['path2data4HOD']},
            'tracer_density_mean': {f'{tracer}': self.OBSample['nbar']},
            'tracer_density_std': {f'{tracer}': 0.1 * self.OBSample['nbar']}
        }
        if chain_path is None:
            chain_path = path_to_HODchain(self.work_dir)
        chain_prefix = f'chain_{clus_ver}_HOD_{version}_'
        chain_params = {
            'chain_prefix': chain_prefix,
            'output_dir': str(chain_path)+'/',
            'nlive': 500,
            'tol': 0.5,
            'labels': self._hod_latex_labels(prior)
        }
        fit_params = {tracer: prior}
        cfgHOD = {
            'sim_params': sim_params,
            'HOD_params': HOD_params,
            'clustering_params': clustering_params,
            'data_params': data_params,
            'chain_params': chain_params,
            'fit_params': fit_params,
            'nthread': 64,
            'prepare_sim': {'Nparallel_load': 18}
        }
        path2cfgHOD = Path(self.work_dir) / "scripts" / "cfgHOD.yaml"
        write_config(cfgHOD, path2cfgHOD)
        ## refresh info
        self.OBSample['zsnap'] = zsnap
        self.HODfit['path2cfgHOD'] = str(path2cfgHOD)
        self.HODfit['path2chain'] = str(chain_path)
        self.HODfit['chain_prefix'] = chain_prefix
        self.HODfit['path2mock'] = str(mock_dir)
        self.HODfit['version'] = version
        self.cfgHOD = cfgHOD
    
    def fit_HOD(
        self,
        time_hms: str='08:00:00',
        ntasks: int=4,
    ) -> None:
        """
        Generate and write the SLURM script for HOD fitting. Remind to prepare the data and configuration file as well.
        """
        from script_HOD import script_HOD
        
        tag = self.OBSample['tag']
        script = script_HOD(
            config_path=self.HODfit['path2cfgHOD'], 
            chain_path=self.HODfit['path2chain'], 
            workdir=self.work_dir,
            version=self.HODfit['version'],
            job_name=f'HODfit_{tag}',
            time_hms=time_hms,
            ntasks=ntasks,
        )
        path_script = self.work_dir / f"scripts/HODfit_{tag}.sh"
        write_script_to_file(script, path_script)
        print("[guide] >>> Submit the script by `sbatch`, it will take several hours. If it's the first time to use this snapshot, remind to delet the `#` before `abacusnbody.hod.prepare_sim_profiles`.\n")

    
    ##### ----- sample HOD parameters ----- #####
    def sample_HOD_params(
        self, 
        chain_root: str | None = None,
        num: int = 100, 
        plot: bool = False,
        cmap: str = 'hsv'
    ) -> np.ndarray:
        """
        Sampling the posterior of the HOD fitting, return the sampled parameter-sets.
        """
        if chain_root is None:
            chain_path=self.HODfit['path2chain']
            chain_prefix=self.HODfit['chain_prefix']
            chain_root = Path(chain_path) / chain_prefix
        ew_sample = np.loadtxt(f"{chain_root}post_equal_weights.dat") # Contains the equally weighted posterior samples. Columns have parameter values followed by loglike value.
        if ew_sample.shape[0] >= num:
            random_indices = np.random.choice(ew_sample.shape[0], size=num, replace=False)
            samples = ew_sample[random_indices][:,:-1]  # exclude the last column (weight)
            print(f"sampled {num} HOD parameter-sets from {ew_sample.shape[0]} equal-weighted samples.")
        else:
            raise ValueError(f"Not enough samples ({ew_sample.shape[0]}) to draw {num} samples.")
        ## refresh info
        self.HIP = {
            'chain_root': str(chain_root),
            'num_samples': num,
            'cmap': cmap,
        }
        self.cfg['HIP'] = self.HIP
        if plot:
            gdsamples = loadMCSamples(chain_root)
            pnames = gdsamples.getParamNames().list()
            ewsamples = MCSamples(samples=ew_sample[:,:-1], names=pnames)
            # mgsamples = MCSamples(samples=samples, names=pnames)
            g = plots.get_subplot_plotter()
            g.triangle_plot([gdsamples, ewsamples], legend_labels=['Original', 'Equal-weighted sample'], filled=False, title_limit=2)
            ## scatter plot with colormap
            idx = np.arange(num)
            nparam = len(pnames)
            for i in range(nparam):
                for j in range(i):
                    ax = g.subplots[i][j]
                    ax.scatter(samples[:, j], samples[:, i], c=idx, cmap=cmap, s=10, edgecolors='k', label=f'i{idx}')
            ## save figure
            g_out = f'{chain_root}resample.png'
            g.export(g_out)
            print(f"resample figure saved to {g_out}")
            
            ## save samples
            np.savetxt(f'{chain_root}resamples.txt', samples, header=','.join(pnames))
            print(f"resampled HOD parameters saved to {chain_root}resamples.txt")
        return samples
    
    def sample_HOD_mocks(
        self, 
        params_list: np.ndarray | None = None,
        nthread: int = 64,
        write_cat: bool = False,
        want_2PCF: bool = False,
        want_poles: bool = True,
    ) -> None:   
        from abacus_helper import AbacusHOD, assign_hod, reset_fic, get_enabled_tracers, compute_mock_and_multipole
        if want_poles:
            from pypower_helpers import run_pypower_redshift
        if self.cfgHOD is None:
            cfgHOD = load_config(self.HODfit['path2cfgHOD'])
        else:
            cfgHOD = self.cfgHOD
        sim_params = cfgHOD['sim_params']
        HOD_params = cfgHOD['HOD_params']
        clustering_params = cfgHOD['clustering_params']
        fit_params = cfgHOD['fit_params']
        mock_dir = self.HODfit['path2mock']
        ### generate AbacusHOD mocks for each sample
        Ball = AbacusHOD(sim_params, HOD_params, clustering_params)

        tracers = get_enabled_tracers(HOD_params)
        tracer = tracers[0]
        for i, sample in enumerate(params_list):
            assign_hod(Ball, fit_params, sample)
            reset_fic(Ball, tracers, nthread=nthread)
            mock, clustering_rsd  = compute_mock_and_multipole(Ball, nthread=nthread)
            if write_cat:
                ## save mock h5
                write_catalogs(Ball, mock, fit_params,out_root=mock_dir, prefix=f'r{i}')
            for tracer, cat in mock.items():
                if want_2PCF:
                    ## save clustering ASCII
                    path2cluster = path_to_clustering(sim_params=sim_params, tracer=tracer, prefix=f'r{i}')
                    np.save(path2cluster, clustering_rsd[f'{tracer}_{tracer}'])
                    print(f"[write] clustering for sample {i} to {path2cluster}")
                if want_poles:
                    x = cat['x']
                    y = cat['y']
                    z = cat['z']
                    poles = run_pypower_redshift(x,y,z)
                    path2poles = path_to_poles(sim_params=sim_params, tracer=tracers[0], prefix=f'r{i}')
                    poles.save(path2poles)
                    print(f"[write] pypower poles for sample {i} to {path2poles}")
    
    
    def sample_HOD_measure_ps(
        self,
        MAP_only: bool = True,
    ) -> None:
        from thecov_helper import read_mock, power_spectrum
        
        tracer = self.OBSample['tracer']
        sim_params = self.cfgHOD['sim_params']
        boxL = 2000.0  # Mpc/h
        boxV = boxL**3  # (Mpc/h)^3
        fname = path_to_catalog(sim_params=sim_params, tracer=tracer, prefix='MAP')
        path2poles = path_to_poles(sim_params=sim_params, tracer=tracer, prefix='MAP')
        pos, nbar = read_mock(fname, boxV=boxV)
        power_spectrum(pos, path2poles=path2poles)
        print(f"[write] pypower poles for sample MAP to {path2poles}")
        ### sampled HOD mocks
        if not MAP_only:
            num = self.HIP['num_samples']
            for i in range(num):
                fname = path_to_catalog(sim_params=sim_params, tracer=tracer, prefix=f'r{i}')
                path2poles = path_to_poles(sim_params=sim_params, tracer=tracer, prefix=f'r{i}')
                pos, nbar = read_mock(fname, boxV=boxV)
                power_spectrum(pos, path2poles=path2poles)
                print(f"[write] pypower poles for sample {i} to {path2poles}")
        
    def sample_HOD_plot_ps(
        self,
        dirEZmocks: Path | None = None,
    ) -> None:
        from load_poles import load_poles_data, load_sampled_HOD_mocks, load_EZmocks

        tracer = self.OBSample['tracer']
        num = self.HIP['num_samples']
        print(f"Number of samples to plot: {num}\n")
        base = 'MAP'
        sim_params = self.cfgHOD['sim_params']
        ### MAP
        data = {
            'MAP': {
                'path': path_to_poles(sim_params=sim_params, tracer=tracer, prefix='MAP'),
                'label': 'MAP', 
                'color': 'black', 
                'lstyle': '-',
                'alpha': 1,
            },
        }
        data, k_1st = load_poles_data(data)
        ### sampled HOD mocks
        data = load_sampled_HOD_mocks(data, k_1st=k_1st, num=num, sim_params=sim_params, tracer=tracer, cmap=self.HIP['cmap'])
        ### EZmocks loading
        if dirEZmocks is not None:
            p0_ez, p0_ez_avg, p0_err = load_EZmocks(dirEZmocks, k_1st=k_1st)
        
        ### define base
        if base in data.keys():
            P0_base = data[base]['p0']
        else:
            raise ValueError(f"Unknown base: {base}")
        
        ### plot
        fig, axs = plt.subplots(2,1,constrained_layout=True,sharex='col',figsize=(8,8),gridspec_kw={'height_ratios': [3, 1]})
        # P0_base = p0_ez_avg if dirEZmocks is not None else P0_base # for test
        if dirEZmocks is not None:
            # top panel: EZmocks
            p = p0_ez[0]
            axs[0].plot(k_1st[1:], p[1:], color='gray', alpha=0.3, label='EZmock')
            for p in p0_ez[1:]:
                axs[0].plot(k_1st[1:], p[1:], color='gray', alpha=0.3)
            axs[0].plot(k_1st[1:], p0_ez_avg[1:], color='gray', lw=2, label='EZmock average')
            # bottom panel: EZmocks fractional errors
            frac_ez = p0_ez_avg / P0_base - 1
            frac_err = p0_err / P0_base 
            axs[1].plot(k_1st[1:], frac_ez[1:], color='gray', lw=2)
            axs[1].fill_between(k_1st[1:], - frac_err[1:], frac_err[1:], color='gray', alpha=0.5, label=r'EZmock $1\sigma$')    
        # top panel: original spectra
        for key in data.keys():
            p0 = data[key]['p0']
            axs[0].plot(k_1st[1:], p0[1:], label=data[key]['label'], color=data[key]['color'], linestyle=data[key]['lstyle'], alpha=data[key]['alpha'])
        axs[0].set_xscale('log')
        axs[0].set_yscale('log')
        axs[0].set_ylabel(r'$P_0(k)$ [$(\mathrm{Mpc}/h)^{3}$]')
        axs[0].legend()
        # bottom panel: fractional errors (P_variant - P_base) / P_base
        for key in data.keys():
            p0 = data[key]['p0']
            frac = p0 / P0_base - 1
            axs[1].plot(k_1st[1:], frac[1:], color=data[key]['color'], linestyle=data[key]['lstyle'], alpha=data[key]['alpha'])
        axs[1].set_xscale('log')
        axs[1].set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
        axs[1].set_ylabel(r'$P^{\rm xx}/P^{\rm base}-1$')
        ylim=0.3
        axs[1].set_ylim(-ylim, ylim)
        axs[1].legend()
        plt.tight_layout()
        fn = self.work_dir / f'mock_ps.png'
        plt.savefig(fn, dpi=300)
        print(f'[plot] -> {fn}')
        ## refresh info
        self.HIP['dirEZmocks'] = str(dirEZmocks)

        
    ##### ----- inference of p ----- #####
    def fit_p_from_mocks(
        self,
        priors: dict[str, dict[str, tuple[float, float]]] = dict(),
        cosmology: str = 'DESI',
        fnl: float = 100,
        mode: str = 'b-p',
        klim: dict[int, list[float]] = {0: [0.003, 0.1]},
        nproc: int = 64,
        write_csv: bool = True,
    ) -> pd.DataFrame:
        """
        Fit p from the HOD mocks, return the best-fit parameters for each mock.
        
        priors: dict of prior settings for each parameter, e.g., {'p': {'limits': (-1., 3.)}, 'sigmas': {'limits': (0., 20.)}}
        fnl: fixed fnl value to the simulation value
        """
        from desilike_helper import fit_p_from_mock_thecov
        
        boxL = 2000.0  # Mpc/h
        boxV = boxL**3  # (Mpc/h)^3
        zsnap = self.OBSample['zsnap']
        num = self.HIP['num_samples']
        # if cosmology == 'DESI':
        #     cosmo = cosmoprimo.fiducial.DESI()
        # else:
        #     raise NotImplementedError(f"cosmology {cosmology} not implemented.")
        theory_dict = {
            'zsnap': zsnap,
            'cosmology': cosmology,
            'mode': mode,
            'fnl': fnl,
            'priors': priors,
        }
        # klin, plin_z = linear_matter_power_spectrum(zeff=zsnap)
        
        ## loop over mocks
        results = []
        with ProcessPoolExecutor(max_workers=min(nproc, num)) as executor:
            futures = {
                executor.submit(fit_p_from_mock_thecov, i, boxV, theory_dict, klim, self.cfgHOD['sim_params'], self.OBSample['tracer']): i
                for i in range(num)
            }
            for future in as_completed(futures):
                results.append(future.result())
        # results = fit_p_from_mock_thecov(0, boxV, theory_dict, klim, self.cfgHOD['sim_params'], self.OBSample['tracer'])  # test single
        # print('results:', results, flush=True)
        ## to DataFrame
        rows = []
        for r in results:
            i, bf = r
            rows.append({'i': i, **bf})
        df_bestfit = pd.DataFrame(rows).sort_values(by='i', ignore_index=True)
        ## save to csv
        if write_csv:
            path_csv = path_to_hip(self.work_dir) / f'fitp_mocks_fnl{fnl}_{cosmology}_{mode}.csv'
            df_bestfit.to_csv(path_csv, index=False)
            print(f"[write] bestfit parameters from HOD mocks to {path_csv}", flush=True)
            self.HIP['path2fitp_csv'] = str(path_csv)
        ## refresh info
        self.HIP['boxsize'] = boxL
        self.HIP['fNL'] = fnl
        self.HIP['cosmology'] = cosmology
        self.HIP['mode'] = mode
        self.HIP['klim'] = klim
        self.HIP['priors'] = priors 
        return df_bestfit
        
    def fit_p_chain(self) -> None:
        """
        Write a bash script to fit p from the HOD mocks.
        """
        from script_HIP import script_HIP
        
        tag = self.OBSample['tag']
        script = script_HIP(num=self.HIP['num_samples'], WORK_DIR=self.work_dir)
        path_script = self.work_dir / f"scripts/run_HIP_chain_{tag}.sh"
        write_script_to_file(script, path_script)
        print("[guide] >>> Run the script on an interactive node, it will take ~ half hours.\n")

    def combine_chains(
        self,
        plot: bool = True,
    ) -> dict:
        """
        Combine the individual fit p chains into one.
        """
        num = self.HIP['num_samples']
        resample_number = 10000
        ### path to chains
        rows = []
        for i in range(100):
            ODIR = self.work_dir / "HIP" / "mocks" / f"r{i}"
            fn_chain = os.path.realpath(ODIR / "chain_zeus")
            rows.append({'i': i, 'fn_chain': str(fn_chain)})
        data = pd.DataFrame(rows)
        ### load and resample each chain
        chain_all = []
        for i in range(num):
            chain = loadMCSamples(data['fn_chain'][i])
            if i==0:
                names = chain.getParamNames().names
                labels = [p.label for p in chain.getParamNames().names]
            weights = chain.weights
            chain_length = len(weights)
            if chain_length != np.sum(weights):
                print(i, "Sum of weights != chain length")
            ### resampling
            if chain_length < resample_number:
                print("Warning: chain length < ", resample_number, ", consider lower resample number!")
            prob = weights / np.sum(weights)
            counts = np.random.multinomial(resample_number, prob)
            resampled_samples = np.repeat(chain.samples, counts, axis=0)
            new_chain = MCSamples(samples=resampled_samples, names=[p.name for p in names])
            chain_all.append(new_chain)
        ### combine all chains 
        samples_list = [c.samples for c in chain_all]
        weights_list = [c.weights if c.weights is not None else np.ones(len(c.samples)) for c in chain_all]
        samples_combined = np.vstack(samples_list)
        weights_combined = np.hstack(weights_list)
        gds_all = MCSamples(samples=samples_combined, names=[p.name for p in names], labels=labels, weights=weights_combined)
        means = gds_all.getMeans()
        cov = gds_all.getCovMat().matrix
        errors = np.sqrt(np.diag(cov))
        ### output
        p_mean = means[0]
        p_error = errors[0]
        p_prior = {'loc': p_mean, 'scale': p_error}
        if plot:
            import matplotlib.colors as mcolors
            
            cmap = plt.get_cmap('hsv')
            norm = mcolors.Normalize()
            idx = np.arange(num)
            colors = cmap(norm(idx))
            g = plots.get_subplot_plotter()
            g.settings.linewidth_contour = 2.0
            g.settings.linewidth = 2.0
            plot_num = 10
            all_samples = chain_all[:plot_num] + [gds_all]
            line_args_list = [{'color':colors[i], 'ls': '-', 'lw':1.0} for i in range(plot_num)] + [{'color':'black', 'ls': '-', 'lw':2.0}]
            legend_labels = [f'Run {i}' for i in range(plot_num)] + ['Combined 100 chains (in equal weights)']
            g = plots.get_subplot_plotter()
            g.triangle_plot(all_samples,
                            params=['p', 'b1', 'sn0', 'sigmas'],
                            filled=False,
                            legend_labels=legend_labels,
                            legend_loc='upper right',
                            contour_args=line_args_list.copy(),
                            line_args=line_args_list.copy(),
                            title_limit=1
                        )
            fn = str(self.work_dir / f'HIP_combined.png')
            g.export(fn)
            print(f"[plot] -> {fn}")
        return p_prior