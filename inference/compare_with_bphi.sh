#!/bin/bash

paths=(
'out/fit_p/QSO-z6_fNL100_base-dv/'
'out/fit_p/QSO-z6_fNL100_base-A-dv/'
'out/fit_p/QSO-z6_fNL100_base-B-dv/'
)

for path in "${paths[@]}"; do
    echo "Processing chain at: $path"
    python scripts/derive_chain.py -p $path
done

python plot_chains/derived_bphi.py
