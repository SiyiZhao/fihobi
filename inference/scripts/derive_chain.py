#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Derive b_phi from the chain with p and b1.
b_phi = 2 * delta_c * (b1 - p), with delta_c = 1.686
Workspace: projects/fihobi/inference/

Usage
-----
$ python ./derive_chain.py -p ${path_to_chain}
"""
import argparse
import sys
sys.path.insert(0, 'source')
from chain_helper import chain

DEFAULT = {}
DEFAULT['path'] = 'out/fit_p/QSO-z6_fNL100_base-dv/'

def derive_bphi(params):
    p = params[0]
    b1 = params[1]
    bphi = 2 * 1.686 * (b1 - p)
    return bphi

def main(path):
    chain_in = chain(path, filename='chain_zeus')
    chain_in.read_pmn()
    chain_in.derive_new_params(derive_bphi, 'bphi', new_para_label='b_{\phi}', filename='chain_zeus_derive_bphi')
    
    
class ArgParseFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass

if __name__ == "__main__":
    # parsing arguments
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=ArgParseFormatter
    )
    parser.add_argument(
        '-p',
        '--path',
        type=str,
        default=DEFAULT['path'],
        help='Path to the chain directory.',
    )
    args = vars(parser.parse_args())
    main(**args)
