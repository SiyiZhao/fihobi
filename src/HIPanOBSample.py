from io_def import (
    load_config, 
    def_OBSample,
    write_script_to_file,
    )

class HIPanOBSample:
    """
    HOD-informed Prior for an Observational Sample.
    """
    def __init__(
        self, 
        cfg_file: str=None,
        tracer: str=None, 
        zmin: float=None, 
        zmax: float=None,
        ) -> None:
        """
        Either provide a configuration file or specify tracer, zmin, and zmax directly.
        """
        ## check tracer validity
        if tracer not in ['QSO', 'LRG']:
            raise ValueError("tracer must be 'QSO' or 'LRG'")
        ## define
        if cfg_file is not None:
            self.cfg_file = cfg_file
            self.cfgs = load_config(cfg_file)
        self.OBSample = def_OBSample(tracer, zmin, zmax)
        self.cfg = {'OBSample': self.OBSample}
    
    
    def measure_clustering(
        self,
        verspec: str='loa-v1',
        version: str='v2/PIP',
        weight_type: str='pip_angular_bitwise',
        path_script: str=None
        ) -> None:
        from clustering import script_clustering

        tracer = self.OBSample['tracer']
        zmin = self.OBSample['zmin']
        zmax = self.OBSample['zmax']
        tag = self.OBSample['tag']
        script = script_clustering(tracer, zmin, zmax, sample_name=tag, verspec=verspec, version=version, weight_type=weight_type)   
        if path_script is not None:
            write_script_to_file(script, path_script)
        # [TBD] run the bash script
        pass 
    
    def prepare_HOD_fitting(self) -> None:
        pass
    
