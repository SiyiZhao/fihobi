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
    bin_params = clustering_params['bin_params']
    rpbins = np.logspace(bin_params['logmin'], bin_params['logmax'], bin_params['nbins']+1)
    pimax = clustering_params['pimax']
    pi_bin_size = clustering_params['pi_bin_size']    # the pi binning is configrured by pi_max and bin size


    # create a new AbacusHOD object
    newBall = AbacusHOD(sim_params, HOD_params, clustering_params)

    # first hod run, slow due to compiling jit, write to disk
    mock_dict = newBall.run_hod(newBall.tracers, want_rsd, write_to_disk = write_to_disk, Nthread = Nthread)

    wp = newBall.compute_wp(mock_dict, rpbins, pimax, pi_bin_size, Nthread = Nthread)
    print(wp, file=open(outdir + 'wp_{:.2f}.npy'.format(newBall.tracers['LRG']['alpha']), 'w'))

    # run the 10 different HODs for timing
    for i in range(10):
        newBall.tracers['LRG']['alpha'] += 0.01
        print("alpha = ",newBall.tracers['LRG']['alpha'])
        start = time.time()
        mock_dict = newBall.run_hod(newBall.tracers, want_rsd, write_to_disk = False, Nthread = 64)
        print("Done iteration ", i, "took time ", time.time() - start)
        wp = newBall.compute_wp(mock_dict, rpbins, pimax, pi_bin_size, Nthread = Nthread)
        print(wp, file=open(outdir + 'wp_{:.2f}.npy'.format(newBall.tracers['LRG']['alpha']), 'w'))

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
