import sys, yaml

path2config=sys.argv[1]
odir=sys.argv[2]
z = 3.0
## prior
p_mean = 1.884
p_sigma = 0.1056 * 3
## data
abacus_poles = '/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks_base-A_v2/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z3p000/MAP_QSO_pypower_poles.npy'

configs = {
    'odir': odir,
    'redshift': z,
    'mode': 'b-p',
    'klim0': [0.003, 0.1],
    'n_EZmocks': 1000,
    
    'input': {
        'abacus_poles': abacus_poles,
        'ezmock_poles': '/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z6_c302/'
    },
    'prior': {
        'p': {
            'dist': 'norm',
            'loc': p_mean,
            'scale': p_sigma,
            'limits': [0, 4]
        },
        'sigmas': {
            'limits': [0, 20.]
        }
    }
}
with open(path2config, 'w', encoding='utf-8') as f:
    yaml.safe_dump(configs, f, sort_keys=False, allow_unicode=True)
print(f"Configuration written to {path2config}")