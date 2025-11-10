# require: 
# 1. paths to fftw2 and gsl libraries
# 2. glass file: conf_2lpt/glass1_le, conf_2lpt/abacus_c000_tk.dat

import os, subprocess
from pathlib import Path

def generate_2lpt_param(
    seed: int,
    redshift: float,
    fnl: float,
    Ngrid: int = 512,
    Lbox: int = 2000,
    fix_amp: int = 0,
    output_path: str | None = None,
) -> str:
    """
    Build a parameter file (as text) and optionally write it to `output_path`.
    
    Parameters
    ----------
    fix_amp : int
        Whether to fix the amplitude of the initial conditions.
        0: no (default), 1: yes.
    """

    script = f"""Nmesh         {Ngrid}     
Nsample       {Ngrid}                                    
Box           {Lbox}
FileBase      ics_{Ngrid}_{Lbox}
OutputDir     /pscratch/sd/s/siyizhao/no_need_of_dir
GlassFile     conf_2lpt/glass1_le
GlassTileFac  {Ngrid}     

Omega               0.315192      
OmegaLambda         0.684808      
OmegaBaryon         0.0493    
OmegaDM_2ndSpecies  0.00      	    
HubbleParam         0.6736       
Sigma8              0.819
PrimordialIndex     0.9649         
Redshift            {redshift}  
Fnl                 {fnl}

FixedAmplitude   {fix_amp}         
PhaseFlip        0         
SphereMode       0         
                                                      
WhichSpectrum    0         
FileWithInputSpectrum    conf_2lpt/no_need_of_file.txt
InputSpectrum_UnitLength_in_cm  3.085678e24 
ShapeGamma       0.201     
WhichTransfer    2        
FileWithInputTransfer     conf_2lpt/abacus_c000_tk.dat

Seed             {seed}       

NumFilesWrittenInParallel 1   

UnitLength_in_cm          3.085678e24
UnitMass_in_g             1.989e43      
UnitVelocity_in_cm_per_s  1e5           

WDM_On               0      
WDM_Vtherm_On        0                                                              
WDM_PartMass_in_kev  10.0   
""".lstrip()

    if output_path:
        outp = Path(output_path)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(script, encoding="utf-8")

    return script

def run_disp_2lpt(seed, redshift, fnl, Ngrid=512, Lbox=2000, fix_amp=0):
    '''
    Generate 2LPT displacement field for given seed, redshift, fnl.
    LOG: logs/2lpt_r{seed}.log
    '''
    ### prepare parameter file for 2LPTnonlocal --------------------------------
    fn_config = f'conf_2lpt/params_2lpt/r{seed}.param'
    generate_2lpt_param(seed=seed, redshift=redshift, fnl=fnl, Ngrid=Ngrid, Lbox=Lbox, fix_amp=fix_amp, output_path=fn_config)
    print(f"Generated {fn_config}", flush=True)
    
    ### prepare displacement field with 2LPTnonlocal ---------------------------
    print(f'Generating 2LPT displacement field for seed {seed}...', flush=True)

    home = os.path.expanduser("~")
    cmd = [
        f"{home}/lib/2LPTic_PNG/2LPTnonlocal",
        fn_config
    ]
    # fftw2 and gsl paths: build LD_LIBRARY_PATH for the child process only
    new_ld = f"{home}/lib/fftw-2.1.5/lib:{home}/.conda/envs/ezmock_png/lib"

    # Use a snapshot of os.environ for subprocess.run and ensure single-threaded
    env = os.environ.copy()
    if env.get("LD_LIBRARY_PATH"):
        env["LD_LIBRARY_PATH"] = new_ld + ":" + env.get("LD_LIBRARY_PATH")
    else:
        env["LD_LIBRARY_PATH"] = new_ld
    env.setdefault("OMP_NUM_THREADS", "1")

    # Run the external program and let it inherit the caller's stdout/stderr
    # so output goes to the same place as the caller (terminal or redirected file).
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"2LPT failed for seed {seed}, returncode {e.returncode}.", flush=True)
        raise

    print('Done. Displacement field saved to /pscratch/sd/s/siyizhao/2LPTdisp/.', flush=True)


