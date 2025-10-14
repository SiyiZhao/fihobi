#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An example script to generate the vsmear CDF file (contain vbin, pdf, cdf of log10|dv| from repeat observations) for a given tracer and redshift range.
"""


from Y3_redshift_systematics import vsmear_modelling 

tracer = 'QSO'
output_dir = '../data/dv_draws'

qso_bins = {'z1': (0.8, 1.1), 'z2': (1.1, 1.4), 'z3': (1.4, 1.7),'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}

for tag, (zmin, zmax) in qso_bins.items():
    print(f"Generating vsmear CDF for {tracer} in redshift range {zmin} - {zmax}")
    vsmear_modelling(tracer, zmin, zmax, dvfn=output_dir)