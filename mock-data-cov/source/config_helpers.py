from pathlib import Path

def generate_2lpt_param(
    seed: int,
    redshift: float,
    fnl: float,
    fix_amp: int = 0,
    output_path: str | None = None,
) -> str:
    """
    Build a parameter file (as text) and optionally write it to `output_path`.
    """

    script = f"""Nmesh         256     
Nsample       256                                    
Box           2000
FileBase      ics_256_2000
OutputDir     /pscratch/sd/s/siyizhao/no_need_of_dir
GlassFile     configs/glass1_le
GlassTileFac  256     

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
FileWithInputSpectrum    configs/no_need_of_file.txt
InputSpectrum_UnitLength_in_cm  3.085678e24 
ShapeGamma       0.201     
WhichTransfer    2        
FileWithInputTransfer     configs/abacus_c000_tk.dat

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
