#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a script for generating HOD mock catalogs.

Refer: abacusutils/scripts/hod/run_hod.py

Usage
-----
$ python ./mock.py --help
"""

import os
import time
import yaml
import numpy as np
import argparse

from abacusnbody.hod.abacus_hod import AbacusHOD

DEFAULTS = {}
DEFAULTS['path2config'] = 'config/abacus_hod.yaml'

def main(path2config):

    Nthread = os.cpu_count()
    print("Number of threads set to:", Nthread)

    # load the config file and parse in relevant parameters
    config = yaml.safe_load(open(path2config))
    sim_params = config['sim_params']
    HOD_params = config['HOD_params']
    clustering_params = config['clustering_params']

    outdir = sim_params['output_dir']

    # additional parameter choices
    want_rsd = HOD_params['want_rsd']
    write_to_disk = HOD_params['write_to_disk']

    # load the rp pi binning from the config file
    rp_bin_params = clustering_params['bin_params']
    wp_num = rp_bin_params['nbins']
    rpbins = np.logspace(rp_bin_params['logmin'], rp_bin_params['logmax'], wp_num+1)
    pimax = clustering_params['pimax']
    pi_bin_size = clustering_params['pi_bin_size']    # the pi binning is configrured by pi_max and bin size
    sbin_params = clustering_params['sbin_params']
    xi_num = sbin_params['nbins']
    sbins = np.logspace(sbin_params['logmin'], sbin_params['logmax'], xi_num+1)
    nbins_mu = clustering_params['mu_bin_size']  


    # create a new AbacusHOD object
    newBall = AbacusHOD(sim_params, HOD_params)

    # first hod run, slow due to compiling jit, write to disk
    mock_dict = newBall.run_hod(newBall.tracers, want_rsd, write_to_disk = write_to_disk, Nthread = Nthread)

    wp = newBall.compute_wp(mock_dict, rpbins, pimax, pi_bin_size, Nthread = Nthread)
    wp_LRG = wp['LRG_LRG']
    np.savetxt(outdir + 'wp_LRG.txt', wp_LRG)

    multipole = newBall.compute_multipole(
        mock_dict, sbins, nbins_mu, orders=[0,2], Nthread=Nthread
    )
    multipole_LRG = multipole['LRG_LRG']
    # xi0_LRG = multipole_LRG[wp_num:wp_num+xi_num]
    xi0_LRG = multipole_LRG[:xi_num]  # xi0 is the first element in the multipole array
    xi2_LRG = multipole_LRG[xi_num:2*xi_num]  # xi2 is the second element in the multipole array
    np.savetxt(outdir + 'xi0_LRG.txt', xi0_LRG)
    np.savetxt(outdir + 'xi2_LRG.txt', xi2_LRG)
    NgalDict, FsatDict = newBall.compute_ngal(newBall.tracers, Nthread=16)
    
    print(NgalDict['LRG'], file=open(outdir + 'Ngal.txt', 'w'))
    # run the 10 different HODs for timing
    # for i in range(10):
    #     newBall.tracers['LRG']['alpha'] += 0.01
    #     print("alpha = ",newBall.tracers['LRG']['alpha'])
    #     start = time.time()
    #     mock_dict = newBall.run_hod(newBall.tracers, want_rsd, write_to_disk = False, Nthread = 64)
    #     print("Done iteration ", i, "took time ", time.time() - start)
    #     start = time.time()
    #     multipole = newBall.compute_multipole(
    #         mock_dict, sbins, nbins_mu, orders=[0,2], Nthread=Nthread
    #     )
    #     print("Done iteration ", i, "clustering took time ", time.time() - start)
    #     wp = newBall.compute_wp(mock_dict, rpbins, pimax, pi_bin_size, Nthread = Nthread)
        # print(wp, file=open(outdir + 'wp_{:.2f}.npy'.format(newBall.tracers['LRG']['alpha']), 'w'))

class ArgParseFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass

if __name__ == '__main__':
    # parsing arguments
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=ArgParseFormatter
    )
    parser.add_argument(
        '--path2config', help='Path to the config file', default=DEFAULTS['path2config']
    )
    args = vars(parser.parse_args())
    main(**args)
