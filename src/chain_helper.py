import numpy as np
import os
from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt
from io_def import plot_style
plot_style()

class chain:
    '''
    Derive new parameters of the chain, and plot them together.
    '''
    def __init__(self, outdir, filename='/_', param_name=None, param_label=None):
        '''
        outdir, filename: output directory & filename.
        
        Can leave None, and then read from .paramnames file:
        param_name: list of param names. 
        param_label: LaTeX labels of param names.
        '''
        self.outdir = outdir
        self.filename = filename
        self.param_name = param_name
        self.param_label = param_label
        
        if not os.path.exists(self.outdir):
            raise FileNotFoundError(f"The dir {self.outdir} does not exist, please prepare the chain first!")
        gdsamples = loadMCSamples(self.outdir+self.filename)   
        self.gdsamples = gdsamples
        
    def read_pmn(self):
        '''
        read the chain from pymultinest.
        
        [root].txt: weight like param1 param2 param3 ...
        [root].paramnames: param label, e.g. logMq \\log M_q (param and label must be separated by the first space)
        '''
        pmn_chain = self.outdir + self.filename + ".txt"
        self.chain = np.loadtxt(pmn_chain)
        ## read .paramnames file
        pmn_par = self.outdir + self.filename + ".paramnames"
        name = []
        label = []
        with open(pmn_par, 'r') as f:
            for line in f:
                parts = line.split(" ",1)
                if len(parts) == 2:
                    name.append(parts[0])
                    label.append(parts[1].strip())
                else:
                    print("Line format error: ", line)  
        self.param_name = name
        self.param_label = label
                
    def best_fit(self):
        '''
        return the best fit parameters.
        '''
        # best_fit = self.chain[np.argmax(self.chain[:,0])]
        # return best_fit[2:]  # exclude weight and -loglike
        ## max weight
        samples, weights = self.gdsamples.samples, self.gdsamples.weights
        max_weight_idx = np.argmax(weights)
        max_logwt_sample = samples[max_weight_idx]
        print('MAP:', max_logwt_sample)
        return max_logwt_sample  

    
    def derive_new_params(self, derive_func, new_para, new_para_label=None, filename='/derived_'):
        '''
        derive a new parameter from the chain.
        write the new chain to a new file.
        also write a new .paramnames file.
        new_para: str, new parameter name.
        '''
        params_chain = self.chain[:, 2:]
        new_param_chain = []
        for params in params_chain:
            new_param = derive_func(params)
            new_param_chain.append(new_param)
        new_chain = np.hstack((self.chain, np.array(new_param_chain).reshape(-1,1)))
        self.chain = new_chain
        self.filename = filename
        ## write .txt file
        np.savetxt(self.outdir + filename + ".txt", new_chain)
        print(f"new chain written.")
        ## write .paramnames file
        if new_para_label is None:
            new_para_label = new_para
        self.param_name.append(new_para+'*') # mark the derived parameters as GetDist convention
        self.param_label.append(new_para_label)
        pmn_par = self.outdir + self.filename + ".paramnames"
        with open(pmn_par, 'w') as f:
            for name, label in zip(self.param_name, self.param_label):
                f.write(f"{name} {label}\n")
        print(f"new param names written.")
        
    def plot_result(self, plot_path=None):
        'plot the result.'
          
        g = plots.get_subplot_plotter()
        g.triangle_plot(self.gdsamples, filled=True, title_limit=1)
        if plot_path is not None:
            plt.savefig(plot_path)
            print(f"plot saved to {plot_path}")
        else:
            plt.show()
        plt.close()

