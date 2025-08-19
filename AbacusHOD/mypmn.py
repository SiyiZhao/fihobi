import os
import pymultinest as pmn
from getdist import plots, loadMCSamples
import matplotlib.pyplot as plt

############# class: my_pmn ##############
class my_pmn:
    '''
    only for flat prior.
    '''
    def __init__(self, prior, log_likelihood, outdir, filename='_', param_label=None, live_points=100, tol=0.5, verbose=True):
        '''
        prior: dict, {param: Any, (low, high) for flat prior}.
        log_likelihood: function, log_likelihood(param).
        outdir, filename: output directory & filename.
        param_label: LaTeX labels of param names.
        live_points, tol, verbose: multinest settings.
        '''
        self.prior = prior
        self.param_num = len(prior)
        self.param_name = list(prior.keys())
        self.log_likelihood = log_likelihood
        self.outdir = outdir
        self.filename = filename
        self.param_label = param_label
        self.live_points = live_points
        self.tol = tol
        self.verbose = verbose
        
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir, exist_ok=True)
        print(f"pymultinest to {self.outdir}")
    
    def write_prior_file(self):
        'write param names and prior ranges.'
        # 写入 .paramnames 文件
        if self.param_label is None:
            self.param_label = self.param_name
        pmn_par = self.outdir + self.filename + ".paramnames"
        with open(pmn_par, 'w') as f:
            for name, label in zip(self.param_name, self.param_label):
                f.write(f"{name} {label}\n")
        # 写入 .ranges 文件
        pmn_prior = self.outdir + self.filename + ".ranges"
        with open(pmn_prior, 'w') as f:
            for name, (low, high) in self.prior.items():
                f.write(f"{name} {low} {high}\n")
        print(f"param names and ranges written.")
    
    def run_pmn(self, prior_transform=None):
        'run multinest. If prior_transform is None, flat prior is assumed.'
        if prior_transform is None:
            def prior_transform(cube, ndim, nparams):
                for i in range(self.param_num):
                    val_max=self.prior[self.param_name[i]][1]
                    val_min=self.prior[self.param_name[i]][0]
                    cube[i] = cube[i] * (val_max - val_min) + val_min
                    
        def loglike(cube, ndim, nparams):
            param=cube[0: self.param_num]
            param_=[]
            for kk in range(len(param)):
                param_.append(param[kk])
            try:
                log_like_value = self.log_likelihood(param_)
                return log_like_value
            except:
                return -1e101

        pmn.run(loglike, 
            prior_transform, 
            self.param_num, 
            outputfiles_basename = self.outdir+self.filename,  ## path for output files, ensure it exits.
            resume=False,
            verbose = self.verbose, 
            n_live_points = self.live_points, 
            evidence_tolerance = self.tol,
            seed=70, 
            n_iter_before_update = 50, 
            importance_nested_sampling = False,
            )
        print("Done pymultinest.")

    def plot_result(self, plot_path=None):
        'plot the result.'
        samples = loadMCSamples(self.outdir+self.filename, settings={'ignore_rows':0.01})     
        if plot_path is None:
            plot_path = self.outdir+'plot.png'
        g = plots.get_subplot_plotter()
        g.triangle_plot(samples, filled=True, title_limit=1)
        plt.savefig(plot_path)
        print(f"plot saved to {plot_path}")
        plt.close()
        