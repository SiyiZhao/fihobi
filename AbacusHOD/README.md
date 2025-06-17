# Mocks with AbacusHOD

Here we generate galaxy mocks using AbacusHOD. 

## Pre-requisites

### AbacusUtils

You need the package `AbacusUtils` to read the files in the data products of AbacusSummit. 
AbacusHOD is a part of this package.
For DESI members, refer to the [wiki](https://desi.lbl.gov/trac/wiki/CosmoSimsWG/Abacus#AbacusSummit).

On `NERSC`, in brief, you may need first load the **environment** by 
```sh
source /global/common/software/desi/desi_environment.sh
```
Then I forked https://github.com/abacusorg/abacusutils.git and git cloned it to my `~/lib` directory.
```sh
git clone https://github.com/SiyiZhao/abacusutils.git
cd abacusutils
pip install -U -e ./
```

### CorrFunc

`AbacusUtils` uses `CorrFunc` to compute the correlation functions. [Corrfunc](https://github.com/manodeep/Corrfunc) can be easily installed by following the [guide in ReadMe](https://github.com/manodeep/Corrfunc?tab=readme-ov-file#method-1-source-installation-recommended).

I installed it into `$HOME/lib` and added the path to the enviroment variable `PYTHONPATH`:
```sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib
```

## Works

### Mock generation & verification

We first generate a mock using the `AbacusHOD` with the parameters shown in [Yuan et al. 2024](https://arxiv.org/abs/2306.06314) to verify our pipeline.

Take LRG in $0.6<z<0.8$ as an example. 
We take the simplest model "Zheng07+fic" in Table 3 of the paper. 
The mean values of the HOD parameters are $\log M_{\rm cut}=12.78$, $\log M_1=13.94$, $\sigma=0.17$, $\alpha=1.07$, $\kappa=0.55$.
We perform the HOD model on the snapshot $z=0.8$ of `AbacusSummit_base_c000_ph000_box`, as described in the paper. 
We compare the projected correlation function $w_p(r_p)$ with the Fig.8 (b) left panel. The results are 

![](plot/wp.png)

The blue dots are the data they used for HOD fitting, and are available in [zenodo](https://zenodo.org/records/7972387). 
Our bins are slightly different from their bins, but the results are consistent. The first dot has poor covariance (the diagonal element is 0), and is not used in the fitting.
They use the log-midpoint of the bins as the $r_p$ values, so the comparison should be taken between the blue and green dots, while we also plot orange dots with the linear-midpoint as the bin center for reference.


### HOD fitting with Y3 data



## Notes on AbacusHOD

[doc](https://abacusutils.readthedocs.io/en/latest/hod.html)

The `mass` refers to host halo mass and is in units of Msun/h. The `id` refers to halo id, and the `Ncent` key refers to number of central galaxies for that tracer. The first `Ncent` galaxies in the catalog are always centrals and the rest are satellites.