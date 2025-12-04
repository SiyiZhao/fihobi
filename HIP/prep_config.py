#!/usr/bin/env python
# coding: utf-8
"""
This is a script for preparing the configuration file of HOD-informed prior.

Usage
-----
$ python prep_config.py

Author: Siyi Zhao
"""
import argparse
import yaml

def arg_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fnl', type=int, default=100, help='Value of fnl')
    parser.add_argument('--z', type=float, default=3.0, help='Redshift')
    parser.add_argument('--tracer', type=str, default='QSO', help='Tracer type')
    parser.add_argument('--ztag', type=str, default='z6', help='Redshift tag')
    parser.add_argument('--hod', type=str, default='base', help='HOD model prefix')
    parser.add_argument('--want_dv', type=bool, default=False, help='Include dv in HOD model')
    parser.add_argument('--Assembly', type=bool, default=False, help='Include Assembly in HOD model')
    parser.add_argument('--BiasENV', type=bool, default=False, help='Include BiasENV in HOD model')
    parser.add_argument('--version', type=str, default='v2.1', help='Version')
    parser.add_argument('--fout', type=str, default='HIP.yaml', help='Output file name')
    return parser

zbins = {
    'LRG': {'z1': (0.4, 0.6), 'z2': (0.6, 0.8), 'z3': (0.8, 1.1)},
    'QSO': {'z1': (0.8, 1.1), 'z2': (1.1, 1.4), 'z3': (1.4, 1.7), 'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}
}


def write_configs_HIP(fnl=100, z=3.0, tracer='QSO', ztag='z6', hod='base', want_dv=False, Assembly=False, BiasENV=False, version="v2.1", fout='HIP.yaml') -> dict: 
    zmin, zmax = zbins[tracer][ztag]
    configs = {
        'fnl': fnl,
        'galaxy': {
            'redshift': z,
            'tracer': tracer,
            'ztag': ztag,
            'zmin': zmin,
            'zmax': zmax,
        },
        'HOD': {
            'prefix': hod,
            'want_dv': want_dv,
            'Assembly': Assembly,
            'BiasENV': BiasENV,
            'version': version,
            'data_dir': "/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v2_rp6s11/",
            'fit_dir': "/pscratch/sd/s/siyizhao/desi-dr2-hod/",
        },
        'sampleHOD': {
            'num': 10,
            'cmap': 'viridis'
        }
    }
    with open(fout, 'w', encoding='utf-8') as f:
        yaml.safe_dump(configs, f, sort_keys=False, allow_unicode=True)
    print(f"Configuration written to {fout}")
    return configs

if __name__ == "__main__":
    parser = arg_parser()
    args = parser.parse_args()
    write_configs_HIP(**vars(args))