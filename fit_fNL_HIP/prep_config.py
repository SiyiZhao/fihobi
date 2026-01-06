import sys, yaml

path2config=sys.argv[1]
odir=sys.argv[2]
z = 3.0
## prior
p_mean = 1.91
p_sigma = 0.36
fix_p = True
p_fixed_value = 1.4
## data
# cov_mode = 'EZmocks'
cov_mode = 'thecov_box'
### data: EZmocks
abacus_poles = '/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks_base-A_v2/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z3p000/MAP_QSO_pypower_poles.npy'
ezmock_poles = '/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z6_c302_fnl300/'
n_EZmocks = 1000
## data: thecov
box_volume = 2000.0**3  # (Mpc/h)^3
abacus_catalog = '/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks_base-A_v2/abacus_HF/DR2_v2.0/Abacus_pngbase_c300_ph000/Boxes/QSO/z3p000/abacus_HF_QSO_3p000_DR2_v2.0_Abacus_pngbase_c300_ph000_MAP_clustering.dat.h5'

configs = {
    'odir': odir,
    'redshift': z,
    'mode': 'b-p',
    'klim0': [0.003, 0.1],
    
    'input': {},
    'prior': {
        'sigmas': {
            'limits': [0, 20.]
        }
    }
}
if fix_p:
    print(f"Preparing config with fixed p = {p_fixed_value}") 
    configs['fix_p'] = fix_p
    configs['p_fixed_value'] = p_fixed_value
else:
    configs['prior']['p'] = {
        'dist': 'norm',
        'loc': p_mean,
        'scale': p_sigma,
        'limits': [0, 4]
    }
if cov_mode == 'EZmocks':
    configs['cov_mode'] = cov_mode
    configs['n_EZmocks'] = n_EZmocks
    configs['input']['abacus_poles'] = abacus_poles
    configs['input']['ezmock_poles'] = ezmock_poles
elif cov_mode == 'thecov_box':
    configs['cov_mode'] = cov_mode
    configs['input']['box_volume'] = box_volume
    configs['input']['abacus_catalog'] = abacus_catalog

with open(path2config, 'w', encoding='utf-8') as f:
    yaml.safe_dump(configs, f, sort_keys=False, allow_unicode=True)
print(f"Configuration written to {path2config}")