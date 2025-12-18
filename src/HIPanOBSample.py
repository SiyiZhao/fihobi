import numpy as np
import pandas as pd
import time, os, logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from getdist import loadMCSamples, MCSamples, plots
from io_def import (
    ensure_dir,
    load_config, 
    write_config,
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
from desilike_helper import prepare_theory, bestfit_p_inference, sampler_inference
from thecov_helper import read_mock, power_spectrum, thecov_box

logging.basicConfig(
    level=logging.INFO,
    format='[%(process)d] %(asctime)s %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler()  # 可以改成 logging.FileHandler("log.txt") 写入文件
    ]
)

THIS_REPO = Path(__file__).parent.parent

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
        '''
        The default seeting is only to write the pypower poles. 
        However, currently pypower and AbacusHOD works in different environments, so we recommend to write_cat=True and want_poles=False.
        '''
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
                write_catalogs(Ball, mock, fit_params,out_root=mock_dir, custom_prefix=f'r{i}')
            for tracer, cat in mock.items():
                if want_2PCF:
                    ## save clustering ASCII
                    path2cluster = path_to_clustering(sim_params=sim_params, tracer=tracer, prefix=f'r{i}')
                    np.save(path2cluster, clustering_rsd[f'{tracer}_{tracer}'])
                    print(f"[write] clustering for sample {i} to {path2cluster}")
                if want_poles:
                    pos = np.stack((cat['x'], cat['y'], cat['z']), axis=-1)
                    path2poles = path_to_poles(sim_params=sim_params, tracer=tracers[0], prefix=f'r{i}')
                    power_spectrum(pos, path2poles=path2poles)
                    print(f"[write] pypower poles for sample {i} to {path2poles}")
    
    def _fit_p_from_mock_thecov(
        self, 
        i: int, 
        boxV: float, 
        theory_dict: dict, 
        klim: dict,
        inference: str,
    ) -> dict:
        """Fit p for a single mock, used in parallel processing.
        The covariance is estimated by thecov.
        inference: 'bestfit' or 'chain'.
        """
        start = time.time()
        pid = os.getpid()
        logging.info(f"Mock {i} start (PID={pid})")

        fname = path_to_catalog(sim_params=self.cfgHOD['sim_params'], tracer=self.OBSample['tracer'], custom_prefix=f'r{i}')

        pos, nbar = read_mock(fname, boxV=boxV)
        data = power_spectrum(pos)
        cov = thecov_box(pk_theory=data, nbar=nbar, volume=boxV, has_shotnoise_set=False)
        theory = prepare_theory(z=theory_dict['zsnap'], cosmology=theory_dict['cosmology'], mode=theory_dict['mode'], fnl=theory_dict['fnl'], priors=theory_dict['priors'], fix_fNL=True)
        if inference == 'bestfit':
            result_dict = bestfit_p_inference(theory=theory, data=data['P_0'], cov=cov, k=data['k'], klim=klim)
        elif inference == 'chain':
            chain_fn = sampler_inference(theory=theory, data=data['P_0'], cov=cov, k=data['k'], klim=klim, odir=self.path2HIP / f'mock_{i}')
            result_dict = {'chain_fn': chain_fn}
        else:
            raise ValueError(f"inference method {inference} not recognized.")
        end = time.time()
        logging.info(f"Mock {i} done (PID={pid}), elapsed {end - start:.3f}s")
        return i, result_dict
    
    def fit_p_from_mocks(
        self,
        num: int | None = None,
        priors: dict[str, dict[str, tuple[float, float]]] = dict(),
        cosmology: str = 'DESI',
        fnl: float = 100,
        mode: str = 'b-p',
        klim: dict[int, list[float]] = {0: [0.003, 0.1]},
        nproc: int = 64,
        inference: str = 'bestfit',
        write_csv: bool = True,
    ) -> pd.DataFrame:
        """
        Fit p from the HOD mocks, return the best-fit parameters for each mock.
        
        priors: dict of prior settings for each parameter, e.g., {'p': {'limits': (-1., 3.)}, 'sigmas': {'limits': (0., 20.)}}
        fnl: fixed fnl value to the simulation value.
        inference: 'bestfit' to use Minuit Profiler to find bestfit parameters; 'chain' to use Zeus Sampler to generate chains.
        write_csv: whether to write the results to a csv file.
        """
        
        boxL = 2000.0  # Mpc/h
        boxV = boxL**3  # (Mpc/h)^3
        zsnap = self.OBSample['zsnap']
        if num is None:
            num = self.HIP['num_samples']
        else:
            self.HIP['num_samples'] = num
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
        path2HIP = path_to_hip(self.work_dir)
        self.path2HIP = path2HIP
        ## loop over mocks
        results = []
        with ProcessPoolExecutor(max_workers=min(nproc, num)) as executor:
            futures = {
                executor.submit(self._fit_p_from_mock_thecov, i, boxV, theory_dict, klim, inference): i
                for i in range(num)
            }
            for future in as_completed(futures):
                results.append(future.result())
        # results = self._fit_p_from_mock_thecov(0, boxV, theory_dict, klim, inference)  # for test
        print('results:', results, flush=True)
        if inference == 'bestfit':
            ## to DataFrame
            rows = []
            for r in results:
                i, bf = r
                rows.append({'i': i, **bf})
            df_fitp = pd.DataFrame(rows).sort_values(by='i', ignore_index=True)
        elif inference == 'chain':
            rows = []
            for r in results:
                i, res = r
                rows.append({'i': i, 'chain_fn': res['chain_fn']})
            df_fitp = pd.DataFrame(rows).sort_values(by='i', ignore_index=True)
        else:
            raise ValueError(f"inference method {inference} not recognized.")
        ## save to csv
        if write_csv:
            path_csv = path2HIP / f'fitp_mocks_fnl{fnl}_{cosmology}_{mode}_{inference}.csv'
            df_fitp.to_csv(path_csv, index=False)
            print(f"[write] bestfit parameters from HOD mocks to {path_csv}", flush=True)
        ## refresh info
        self.HIP['path2hip'] = str(path2HIP)
        self.HIP['boxsize'] = boxL
        self.HIP['fNL'] = fnl
        self.HIP['cosmology'] = cosmology
        self.HIP['mode'] = mode
        self.HIP['klim'] = klim
        self.HIP['priors'] = priors 
        return df_fitp
        