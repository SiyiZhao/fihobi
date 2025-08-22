import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')


def compute_HOD(logM, params):
    'compute HOD for each logM with parameters. f_ic is fixed to 1 currently, TODO: derive f_ic.'
    from scipy.special import erf

    # Unpack parameters
    logMcut, logM1, sigma_logM, alpha, kappa = params[:5]
    f_ic = 1
    # inv_sqrt2 = 0.7071067811865475244
    # ln10 = 2.30258509299404568402
    # mean_ncen = 0.5 * f_ic * (1.0 + erf((ln10*logM - ln10*logMcut)*inv_sqrt2/sigma_logM))
    ln10_inv_sqrt2 = 1.62817353351514684460
    mean_ncen = 0.5 * f_ic * (1.0 + erf((logM - logMcut)*ln10_inv_sqrt2/sigma_logM))
    
    Mcut = 10.**logMcut
    M1 = 10.**logM1
    mass = 10.**logM
    mean_nsat = np.zeros_like(mass)
    idx = np.where(mass - kappa*Mcut > 0)[0]
    mean_nsat[idx] = ((mass[idx] - kappa*Mcut)/M1)**alpha
    mean_nsat *= mean_ncen
    total = mean_ncen + mean_nsat
    return mean_ncen, mean_nsat, total

def weighted_statistics(data, weights):
    'Calculate weighted mean and quantiles'
    from statsmodels.stats.weightstats import DescrStatsW
    
    data = DescrStatsW(data, weights=weights)
    mean = data.mean
    hi68 = data.quantile(0.84, return_pandas=False)
    lo68 = data.quantile(0.16, return_pandas=False)
    hi95 = data.quantile(0.975, return_pandas=False)
    lo95 = data.quantile(0.025, return_pandas=False)
    return mean, hi68, lo68, hi95, lo95

def plot_HOD_stat(samples, weights, path='hod_stat.png', logMcut=None):
    'calculate HOD for each sample and plot the statistics of HOD results.'
    min_logM = 11
    max_logM = 15
    logM = np.linspace(min_logM, max_logM, 1000)
    n_bins = 100

    hod_cen = np.zeros((len(samples), len(logM)))
    hod_sat = np.zeros((len(samples), len(logM)))
    hod_tot = np.zeros((len(samples), len(logM)))
    for i, row in enumerate(samples):
        hod_cen[i], hod_sat[i], hod_tot[i] = compute_HOD(logM, row)

    bin_edges = np.linspace(min_logM, max_logM, n_bins+1)
    bin_indices = np.digitize(logM, bin_edges) - 1
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    cen_mean = np.zeros(n_bins)
    sat_mean = np.zeros(n_bins)
    tot_mean = np.zeros(n_bins)
    cen_hi68 = np.zeros(n_bins)
    sat_hi68 = np.zeros(n_bins)
    tot_hi68 = np.zeros(n_bins)
    cen_lo68 = np.zeros(n_bins)
    sat_lo68 = np.zeros(n_bins)
    tot_lo68 = np.zeros(n_bins)
    cen_hi95 = np.zeros(n_bins)
    sat_hi95 = np.zeros(n_bins)
    tot_hi95 = np.zeros(n_bins)
    cen_lo95 = np.zeros(n_bins)
    sat_lo95 = np.zeros(n_bins)
    tot_lo95 = np.zeros(n_bins)
    for bin_idx in range(n_bins):
        bin_mask = (bin_indices == bin_idx)
        hod_cen_bin = np.nanmean(hod_cen[:, bin_mask], axis=1)
        hod_sat_bin = np.nanmean(hod_sat[:, bin_mask], axis=1)
        hod_tot_bin = np.nanmean(hod_tot[:, bin_mask], axis=1)

        cen_mean[bin_idx], cen_hi68[bin_idx], cen_lo68[bin_idx], cen_hi95[bin_idx], cen_lo95[bin_idx] = weighted_statistics(hod_cen_bin, weights)
        sat_mean[bin_idx], sat_hi68[bin_idx], sat_lo68[bin_idx], sat_hi95[bin_idx], sat_lo95[bin_idx] = weighted_statistics(hod_sat_bin, weights)
        tot_mean[bin_idx], tot_hi68[bin_idx], tot_lo68[bin_idx], tot_hi95[bin_idx], tot_lo95[bin_idx] = weighted_statistics(hod_tot_bin, weights)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlabel(r'$\log (M/M_\odot)$')
    ax.set_ylabel(r'$n [(h/{\rm Mpc})^3]$')
    ax.set_xlim(min_logM, max_logM)
    ax.set_yscale('log')
    ax.set_ylim(1e-2, 1e2)
    # ax.axhline(1, color='gray', linestyle='--')
    if logMcut is not None:
        ax.axvline(logMcut, color='gray', linestyle='--', label=r'$\log M_{\text{cut}}$')
    ax.plot(bin_centers, cen_mean, label='Central Mean', color='blue')
    ax.fill_between(bin_centers, cen_lo68, cen_hi68, color='blue', alpha=0.3, label='Central 68%')
    ax.fill_between(bin_centers, cen_lo95, cen_hi95, color='blue', alpha=0.2, label='Central 95%')
    ax.plot(bin_centers, sat_mean, label='Satellite Mean', color='orange')
    ax.fill_between(bin_centers, sat_lo68, sat_hi68, color='orange', alpha=0.3, label='Satellite 68%')
    ax.fill_between(bin_centers, sat_lo95, sat_hi95, color='orange', alpha=0.2, label='Satellite 95%')
    ax.plot(bin_centers, tot_mean, label='Total Mean', color='green')
    ax.fill_between(bin_centers, tot_lo68, tot_hi68, color='green', alpha=0.3, label='Total 68%')
    ax.fill_between(bin_centers, tot_lo95, tot_hi95, color='green', alpha=0.2, label='Total 95%')
    ax.legend()
    fig.savefig(path, dpi=300, bbox_inches='tight')
    return fig
