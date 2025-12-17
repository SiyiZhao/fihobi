import sys, yaml

path2config=sys.argv[1]
odir=sys.argv[2]
z = 3.0

configs = {
    'odir': odir,
    'redshift': z,
    'mode': 'b-p',
    'klim0': [0.003, 0.1],
    'n_EZmocks': 1000,
    
    'input': {
        'abacus_poles': '/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks_base_v2/Abacus_pngbase_c302_ph000/z3.000/galaxies_rsd/pypower_poles.npy',
        'ezmock_poles': '/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z6_c302/'
    },
    'prior': {
        'p': {
            'dist': 'norm',
            'loc': 1.884,
            'scale': 0.1056
        },
        'sigmas': {
            'limits': [0, 20.]
        }
    }
}
with open(path2config, 'w', encoding='utf-8') as f:
    yaml.safe_dump(configs, f, sort_keys=False, allow_unicode=True)
print(f"Configuration written to {path2config}")