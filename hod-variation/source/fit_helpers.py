# Credit: https://github.com/ahnyu/hod-variation/blob/main/source/pocomc_helpers.py , modified for our use case

import numpy as np
import sys
from pathlib import Path
THIS_REPO = Path(__file__).parent.parent.parent
src_dir = THIS_REPO / 'src'
if src_dir not in sys.path:
    sys.path.insert(0, str(src_dir))
from abacus_helper import assign_hod, reset_fic, set_theory_density

# Global variables to be set once per MPI process.
GLOBAL_BALL = None           
GLOBAL_DATA_OBJ = None       
GLOBAL_CONFIG = None         
GLOBAL_NTHREAD = None   

def generate_prior(fit_params):
    """
    Generate a combined prior and parameter mapping from fit_params using uniform priors.
    
    Here each free parameter is defined as [provided_index, lower_bound, upper_bound] and you must 
    ensure that the provided_index values are globally unique across all tracers.
    
    Returns:
      tuple: (prior, param_mapping) where:
             - prior: A single pc.Prior object constructed from all free parameter uniform distributions,
                      ordered by increasing provided_index.
             - param_mapping: A dictionary keyed by tracer, where each value is a mapping from a parameter 
                      name to its provided (global) index in the combined free-parameter vector.
    """
    all_params = {}
    param_mapping = {}
    prior = {}
    
    for tracer, params in fit_params.items():
        param_mapping[tracer] = {}
        for param, values in params.items():
            provided_index, lb, ub, prior_type = values  # Provided index is assumed to be globally unique.
            if provided_index in all_params:
                raise ValueError(f"Duplicate free parameter index encountered: {provided_index}")
            all_params[provided_index] = [lb, ub]
            param_mapping[tracer][param] = provided_index
            prior[param] = [lb, ub]
    
    return prior, param_mapping

def set_global_objects(data_obj, config, nthread, newBall):
    """
    Set the global objects used by the pocomc_loglike function.
    
    This function must be called once per MPI process before entering the MCMC loop.
    Note: The heavy AbacusHOD instance (GLOBAL_BALL) is NOT passed in here.
    Instead, it will be lazily initialized locally in each MPI process.
    
    Parameters:
      data_obj: An instance of data_object (or similar) holding observed data.
      config: A dictionary with keys "sim_params", "HOD_params", "clustering_params",
              "param_mapping", and "tracers".
      nthread: Number of threads to use.
    """
    global GLOBAL_DATA_OBJ, GLOBAL_CONFIG, GLOBAL_NTHREAD, GLOBAL_BALL
    GLOBAL_DATA_OBJ = data_obj
    GLOBAL_CONFIG = config
    GLOBAL_NTHREAD = nthread
    GLOBAL_BALL = newBall

def log_likelihood(free_params):
    """
    Stand-alone log-likelihood function for the pyMultiNest sampler.
    
    This function assumes the following globals have been set:
      - GLOBAL_DATA_OBJ: data_object instance.
      - GLOBAL_CONFIG: Dict with keys "sim_params", "HOD_params", "clustering_params",
                       "param_mapping", and "tracers".
      - GLOBAL_NTHREAD: Number of threads (integer).
      - GLOBAL_BALL: Expensive AbacusHOD instance; if not already loaded, it is lazily initialized.
    
    Parameters:
      free_params (np.ndarray): Free parameters vector (ordered as in the pocoMC prior).
      
    Returns:
      float: Total log-likelihood.
    """
    global GLOBAL_BALL, GLOBAL_DATA_OBJ, GLOBAL_CONFIG, GLOBAL_NTHREAD

    ball = GLOBAL_BALL
    data_obj = GLOBAL_DATA_OBJ
    config = GLOBAL_CONFIG
    nthread = GLOBAL_NTHREAD
    box_volume = ball.params['Lbox']**3
    for tracer in config["tracers"]:
        for param_name in config["param_mapping"][tracer]:
            mapping_idx = config["param_mapping"][tracer][param_name]
            if free_params[mapping_idx] > config["fit_params"][tracer][param_name][2] or free_params[mapping_idx] < config["fit_params"][tracer][param_name][1]:
                return -np.inf
            
            assign_hod(ball, config["fit_params"], free_params)
                
    for tracer in config["tracers"]:
        if tracer == 'LRG' and 10**ball.tracers[tracer]["logM_cut"]*ball.tracers[tracer]["kappa"]<1e12:
            return -np.inf
        elif tracer == 'QSO'and 10**ball.tracers[tracer]["logM_cut"]*ball.tracers[tracer]["kappa"]<2e11:
            return -np.inf
            
    
    # Reset 'ic' and compute theoretical number density.
    ball, ngal_dict, fsat_dict = reset_fic(ball, config["HOD_params"], GLOBAL_DATA_OBJ.density_mean, nthread=nthread)

    # Control the satellite fraction.
    for tracer in config["tracers"]:
        if fsat_dict[tracer] > 0.6:
            return -np.inf
            
    # Generate mock galaxy catalog.
    mock_dict = ball.run_hod(ball.tracers, ball.want_rsd, Nthread=nthread, verbose=False)

    # Compute theoretical clustering.
    clustering_type = config["clustering_params"].get("clustering_type", "wp").lower()
    if clustering_type == "wp":
        theory_clustering_dict = ball.compute_wp(mock_dict, ball.rpbins, ball.pimax, ball.pi_bin_size, Nthread=nthread)
    elif clustering_type == "all":
        theory_clustering_dict = ball.compute_multipole(
            mock_dict,
            rpbins=ball.rpbins,
            pimax=ball.pimax,
            sbins=ball.rpbins[5:],
            nbins_mu=40,
            Nthread=nthread
        )
    else:
        raise ValueError("Unknown clustering_type: " + clustering_type)

    
    # Compute theoretical density for each tracer.
    box_volume = ball.params['Lbox']**3
    theory_density_dict = set_theory_density(ngal_dict, box_volume, GLOBAL_DATA_OBJ.density_mean, config["tracers"], nthread=nthread)

    # Return total log-likelihood.
    return data_obj.compute_loglike(theory_clustering_dict, theory_density_dict)


