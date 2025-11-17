# source/data_object.py
# Credit: https://github.com/ahnyu/hod-variation/

import numpy as np

class data_object:
    def __init__(self, data_params, hod_params, clustering_params):
        """
        Initializes the data_object by reading data files specified in the parameters.
        
        Parameters:
          data_params (dict): Dictionary with keys:
              - "tracer_combos": mapping composite keys (e.g., "LRG_LRG") to paths:
                  * "path2wp", "path2xi02", and "path2cov"
              - "tracer_density_mean": mapping tracer (e.g., "LRG") to mean density.
              - "tracer_density_std": mapping tracer (e.g., "LRG") to density standard deviation.
          hod_params (dict): Contains a "tracer_flags" dictionary indicating which tracers are active.
          clustering_params (dict): Contains at least the key "clustering_type" (either 'wp' or 'all').
        
        Attributes:
          - self.wp: Dictionary with composite keys → loaded wp arrays (using column 1).
          - self.xi02: Dictionary with composite keys → loaded xi02 arrays (using columns 1 and 3; only if clustering_type=='all').
          - self.cov: Dictionary with composite keys → loaded covariance arrays.
          - self.invcov: Dictionary with composite keys → inverse covariance matrices.
          - self.density_mean: Dictionary keyed by tracer → observed mean densities.
          - self.density_std: Dictionary keyed by tracer → observed density standard deviations.
          - self.clustering: Dictionary with composite keys → flattened clustering data.
            For clustering_type 'wp', it is the flattened wp array;
            for 'all', it is the horizontal concatenation (flattened) of wp and xi02.
        """
        self.wp = {}
        self.xi02 = {}
        self.cov = {}
        self.invcov = {}
        self.density_mean = {}
        self.density_std = {}
        self.clustering = {}

        tracer_flags = hod_params.get("tracer_flags", {})
        active_tracers = [tr for tr, flag in tracer_flags.items() if flag]
        cluster_type = clustering_params.get("clustering_type", "wp").lower()

        density_mean_all = data_params.get("tracer_density_mean", {})
        density_std_all  = data_params.get("tracer_density_std", {})

        for tracer in active_tracers:
            composite_key = f"{tracer}_{tracer}"
            combos = data_params.get("tracer_combos", {})
            if composite_key not in combos:
                print(f"Warning: No data paths for composite key {composite_key}. Skipping tracer {tracer}.")
                continue
            paths = combos[composite_key]
            self.wp[composite_key] = np.loadtxt(paths["path2wp"], usecols=(1))
            if cluster_type == "all":
                self.xi02[composite_key] = np.loadtxt(paths["path2xi02"], usecols=(1, 3))
            self.cov[composite_key] = np.loadtxt(paths["path2cov"])
            if cluster_type == "wp":
                nwpbins = len(self.wp[composite_key])
                self.cov[composite_key] = self.cov[composite_key][:nwpbins,:nwpbins]
            self.invcov[composite_key] = np.linalg.inv(self.cov[composite_key])
            if tracer in density_mean_all:
                self.density_mean[tracer] = density_mean_all[tracer]
            else:
                print(f"Warning: Density mean not found for tracer {tracer}.")
            if tracer in density_std_all:
                self.density_std[tracer] = density_std_all[tracer]
            else:
                print(f"Warning: Density std not found for tracer {tracer}.")

            if cluster_type == "wp":
                self.clustering[composite_key] = np.ravel(self.wp[composite_key])
            elif cluster_type == "all":
                wp_flat = np.ravel(self.wp[composite_key])
                xi02_flat = np.ravel(self.xi02[composite_key], order='F')
                self.clustering[composite_key] = np.hstack([wp_flat, xi02_flat])
            else:
                self.clustering[composite_key] = np.ravel(self.wp[composite_key])

    def compute_loglike(self, theory_clustering, theory_density):
        """
        Compute the total log-likelihood from clustering and density parts.
        
        For clustering:
          For each composite key, the chi2 = (observed - theory).T * invcov * (observed - theory)
          contributes -0.5 * chi2.
        
        For density (assumed Gaussian):
          For each tracer, contribution = -0.5 * ( (obs - theory)² / std² ).
        
        Parameters:
          theory_clustering (dict): Dictionary with composite keys → theoretical clustering data.
          theory_density (dict): Dictionary with tracer keys → theoretical number density.
        
        Returns:
          float: Total log-likelihood.
        """
        loglike_cluster = 0.0
        for comp_key, observed in self.clustering.items():
            if comp_key not in theory_clustering:
                print(f"Warning: No theory clustering for {comp_key}.")
                continue
            diff = observed - theory_clustering[comp_key]
            chi2 = diff.dot(self.invcov[comp_key].dot(diff))
            loglike_cluster += -0.5 * chi2

        loglike_density = 0.0
        for tracer, obs_density in self.density_mean.items():
            if tracer not in theory_density:
                print(f"Warning: No theory density for tracer {tracer}.")
                continue
            if theory_density[tracer] >= obs_density:
                continue  # No penalty if theory density >= observed
            else:
                diff = obs_density - theory_density[tracer]
                std = self.density_std[tracer]
                loglike_density += -0.5 * ( (diff ** 2) / (std ** 2) ) 
        return loglike_cluster + loglike_density
