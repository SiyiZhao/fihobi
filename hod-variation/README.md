# HOD fitting with AbacusUtils

We fit HOD models to DESI DR2 data using AbacusUtils (modified by Hanyu).

## Work Flow

1. Prepare the data, the config files and slurm scripts (follow `prep.sh`)
2. Enter `launchers/` and submit the jobs to NERSC, the launcher scripts contain three steps: 
   1. prepare: prepare the Abacus simulations with the mode of profiles, 
   2. fitting: run nest sampling to fit the HOD model,
   3. post-process: Analyze the chains and get the best-fit parameters (follow `post.sh`, we add it into the slurm script so it will be done automatically after the MCMC sampling is done), generate mock catalogs with the best-fit HOD parameters and measure the correlation functions.
3. Analysis among different fittings (Optional): use `comp_fit.py` to compare the fitting results from different simulations / HOD models. (Pay attention the data vector should be the same among the different fittings you want to compare.)
4. NEXT: post-process has generated the best-fit catalogs, go `../mock-data-cov/` to measure the power spectrum.

## Works have been done with these codes 

1. QSO z=0.8-2.1 ('z0' in our notation), on `AbacusSummit_base_c000_ph000` (fiducial cosmology), base HOD model with dv (redshift error).
2. QSO z=1.7-2.3 ('z4'), on `AbacusSummit_base_c000_ph000`, base HOD model without dv. (rerun with right number density & larger prior)
3. QSO z=1.7-2.3 ('z4'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model without dv.
4. QSO z=1.7-2.3 ('z4'), on `AbacusSummit_base_c000_ph000`, base HOD model with dv.
5. QSO z=1.4-1.7 ('z3'), on `AbacusSummit_base_c000_ph000`, base HOD model w/ & w/o dv.
6. QSO z=0.8-1.1 ('z1'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
7. QSO z=1.1-1.4 ('z2'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
8. QSO z=1.4-1.7 ('z3'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
9. QSO z=1.7-2.3 ('z4'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
10. same as 7, but cut 3 more bins at small scales in wp (from 6) and xi (from 11).
11. same as 9, but cut 3 more bins at small scales in wp (from 6) and xi (from 11).
12. QSO z=2.3-2.8 ('z5') and z=2.8-3.5 ('z6'), start from the 6th rp and 11th s bin (noted as 'rp6s11'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
13. QSO at all 6 redshift bins ('z1', 'z4', 'z6' would have different prior on logM1), in 'rp6s11' mode, on `AbacusSummit_base_c302_ph000`($f_{\rm NL}=100$), base HOD model w/ & w/o dv.



## Pre-requisites

### AbacusUtils

We need the package `AbacusUtils` to read the files of the N-body simulation data products. 
AbacusHOD is a part of this package.
For DESI members, refer to the [wiki](https://desi.lbl.gov/trac/wiki/CosmoSimsWG/Abacus#AbacusSummit).

On `NERSC`, in brief, we may need first load the **environment** by 
```sh
source /global/common/software/desi/desi_environment.sh
```
Then git cloned my fork of `abacusutils` to `$HOME/lib` (or any other place you like) and finally install it.
```sh
git clone https://github.com/SiyiZhao/abacusutils.git
cd abacusutils
pip install -U -e ./
```

==Attention==: We modified it with Hanyu's `hod-variation` [repo](https://github.com/ahnyu/hod-variation/) to enable the use of `use_profiles` (assign satellites with NFW profile) and `want_dv` (add redshift error effect to `z` in RSD mocks) options. So we recommend to use my forked repo. 
(I have also small modifications to Hanyu's code to make sure the codes in this project work well in `desi_enviroment` without virtual environment.)

### CorrFunc

`AbacusUtils` uses `CorrFunc` to compute the correlation functions. [Corrfunc](https://github.com/manodeep/Corrfunc) can be easily installed by following the [guide in ReadMe](https://github.com/manodeep/Corrfunc?tab=readme-ov-file#method-1-source-installation-recommended).

I installed it into `$HOME/lib` and added the path to the enviroment variable `PYTHONPATH`:
```sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib
```

## Others

- On NERSC, in order to reach out the results easily, I have create a link by `ln -sT /pscratch/sd/s/siyizhao/desi-dr2-hod /global/homes/s/siyizhao/projects/fihobi/hod-variation/output/desi-dr2-hod`, so you can find the output files in `./output/desi-dr2-hod/`.