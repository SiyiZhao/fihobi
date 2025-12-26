#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An example script to generate the vsmear CDF file (contain vbin, pdf, cdf of log10|dv| from repeat observations) for a given tracer and redshift range.
"""


from Y3_redshift_systematics import vsmear_modelling 

output_dir = '../data/dv_draws'

# tracer = 'QSO'
# zbins = {'z1': (0.8, 1.1), 'z2': (1.1, 1.4), 'z3': (1.4, 1.7),'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}
tracer = 'LRG'
zbins = {'z1': (0.4, 0.6), 'z2': (0.6, 0.8), 'z3': (0.8, 1.1)}

for tag, (zmin, zmax) in zbins.items():
    print(f"Generating vsmear CDF for {tracer} in redshift range {zmin} - {zmax}")
    vsmear_modelling(tracer, zmin, zmax, dvfn=output_dir)