# HIP of an observational sample

See `hip_an_OBSample.py`

## Work Flow

1. Define observational galaxies sample: LRG/QSO, $z_{\min}$ - $z_{\max}$. eg. `OBSample=QSO_z2p8_3p5`
2. Measure clustering ($w_p, \xi_0, \xi_2$) of the observational sample. eg. `../clustering/run_xirunpc.sh`.
3. Prepare the data and configuration file for HOD fitting. 

### Current running flow
Refer to `hip_anOBS.sh`.

1. `hip_an_OBSample.py` prepares all the scripts and configuration files for both small-scale clustering measurement and HOD fitting.2. Submit the small-scale clustering measurement job. Wait until it's done. Then 