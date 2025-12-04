import yaml

def write_configs_HIP(fnl=100, z=3.0, tracer='QSO', hod='base', want_dv=False, Assembly=False, BiasENV=False, version="v2.1", fout='HIP.yaml'):
    configs = {
        'redshift': z,
        'fnl': fnl,
        'tracer': tracer,
        'HOD': {
            'prefix': hod,
            'want_dv': want_dv,
            'Assembly': Assembly,
            'BiasENV': BiasENV,
            'version': version,
            'data_dir': "/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v2_rp6s11/",
            'fit_dir': "/pscratch/sd/s/siyizhao/desi-dr2-hod/",
        },
    }
    with open(fout, 'w', encoding='utf-8') as f:
        yaml.safe_dump(configs, f, sort_keys=False, allow_unicode=True)
    print(f"Configuration written to {fout}")
    return configs


if __name__ == "__main__":
    write_configs_HIP()