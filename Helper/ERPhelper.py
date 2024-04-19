#!/usr/bin/env python3
"""
@author: meysamhashemi  INS Marseille

"""

import numpy as np
import seaborn as sns
import arviz as az
import matplotlib.pyplot as plt



colors_l = ["#A4C3D9", "#7B9DBF", "#52779F", "#2A537E"] 



def tails_percentile(my_var_names, prior_predictions, thr):
    tails_xth_percentile = {}
    for key, value in prior_predictions.items():
        if key in my_var_names:
            sorted_values = np.sort(value)
            top_xth_percentile = sorted_values[int(0.05 * len(sorted_values))]
            tails_xth_percentile[key] = np.array(top_xth_percentile)
    return tails_xth_percentile




def calcula_map (chains_):
    if chains_.shape[0] <= 1:
        raise ValueError("Expected chains to have shape of n_params * n_samples")
    params_map = []
    for i in range(int(chains_.shape[0])):
        y=chains_[i]
        hist, bin_edges = np.histogram(y, bins=50)  # Adjust the number of bins as needed
        max_bin_index = np.argmax(hist)
        x_value_at_peak = (bin_edges[max_bin_index] + bin_edges[max_bin_index + 1]) / 2
        params_map.append(x_value_at_peak)
    return params_map







def my_axis(ax, params_labels):
    for a in ax[:, 1:].flatten():
        a.set_ylabel('')
    for i, prm_label in enumerate(params_labels):
        ax[i // 5, i % 5].set_xlabel(prm_label, fontsize=16)    




def plot_obsrvation(ts_model, xpy_model, ts_obs, xpy_obs):
    plt.figure(figsize=(6,4))
    plt.plot(ts_model, xpy_model, color="b", lw=2,  alpha=0.8, label='model');
    plt.plot(ts_obs, xpy_obs, color="red", lw=1, marker=".", alpha=0.4, label='observation');
    plt.legend(fontsize=10, frameon=False, loc='upper right')
    plt.ylabel('Voltage [mV]', fontsize=14); 
    plt.xlabel('Time [ms]', fontsize=14); 
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout();
    #plt.savefig(os.path.join((output_dir),"Observation.png"), dpi=800)



def plot_priorcheck(ts_obs, xpy_obs, prior_predictions, n_, title):
    plt.figure(figsize=(6, 5))
    plt.plot(ts_obs, xpy_obs ,'.-', color='b', lw=1, label='observation');
    for i in range(n_):
        plt.plot(ts_obs, prior_predictions['xpy_model'][i], lw=1, alpha=0.2)
    plt.plot(ts_obs, prior_predictions['xpy_model'][i], lw=1, alpha=0.2, label='prior samples')    
    plt.title(title, fontsize=14)
    plt.legend(fontsize=10, frameon=False, loc='upper right')
    plt.ylabel('Voltage [mV]', fontsize=14); 
    plt.xlabel('Time [ms]', fontsize=14); 
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout();



def plot_lp_chains(lp, n_chains, title):

    fig, ax = plt.subplots(figsize=(8, 2))

    ax.plot(lp, label='chaque lp')
    ax.axhline(y=np.mean(lp), color='cyan', linestyle='--', label='Expected lp')
    for i in range(1, n_chains+1):
        x = i * len(lp) // n_chains
        ax.axvline(x, color='red', linestyle='--')
        ax.text(x-100, np.max(lp)-1, f'Chain {i}', color='red', fontsize=10, ha='center')
    plt.ylabel('lp', fontsize=14); 
    plt.xlabel('samples', fontsize=14); 
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend(bbox_to_anchor=(.9, 1), loc='upper left', fontsize=10)
    plt.title(title, fontsize=14)  
    plt.tight_layout();




def plot_posterior_pooled(my_var_names, theta_true, prior_predictions, chains_pooled, title):

    params_map_pooled=calcula_map(chains_pooled)
    
    fig, ax = plt.subplots(ncols=5, nrows=2, figsize=(15, 5))
    for iprm, prm in enumerate(my_var_names) :
        a = ax[iprm//5, iprm%5]
        a.set_xlabel(prm)
        a.axvline(theta_true[iprm], color='r', label='true', linestyle='--')
        a.axvline(params_map_pooled[iprm], color='lightblue', label='MAP', linestyle='--', lw=2.)
        sns.kdeplot(prior_predictions[prm], ax=a, color='lime', alpha=0.5, linestyle='-', lw=2,  label='prior', shade=True)
        sns.kdeplot(chains_pooled[iprm, :], ax=a, color='darkblue', alpha=0.2, linestyle='-', label='pooled chains', lw=2., shade=True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.suptitle(title, fontsize=18) 
    fig.tight_layout(rect=[0, 0, 1, 1])  




def plot_fitted(data, az_obj_posterior):

    ts_obs = data['ts_obs']
    xpy_obs = data['xpy_obs']
    ds = data['ds']

    n_chains = az_obj_posterior.dims['chain']

    fig, axs = plt.subplots(1, 4, figsize=(12, 3))
    for ich in range(n_chains):
        axs[ich].plot(ts_obs, xpy_obs, '.', color='red', lw=3, label='obs')
        axs[ich].plot(ts_obs, az_obj_posterior['xpy_model'][ich, :, :].mean(axis=0), lw=2, color='b', label='fit')
        axs[ich].set_title(f'Fitted data for chain={ich+1}', fontsize=12)
        axs[ich].legend(fontsize=10, frameon=False, loc='upper right')
        axs[ich].set_xlabel('Time [ms]', fontsize=12)
        axs[ich].tick_params(axis='both', which='major', labelsize=10)
        axs[ich].tick_params(axis='both', which='minor', labelsize=8)
        if  ich==0:   
            axs[ich].set_ylabel('Voltage [mV]', fontsize=12)
    plt.tight_layout()





def plot_posteriorcheck(data, xpy_per05_pooled, xpy_per95_pooled, title):
    ts_obs = data['ts_obs']
    xpy_obs = data['xpy_obs']

    plt.figure(figsize=(6, 4))
    plt.plot(ts_obs, xpy_obs, color="red", lw=1, marker=".", alpha=0.4, label='observation');
    plt.fill_between(ts_obs, xpy_per05_pooled, xpy_per95_pooled, linewidth=2,facecolor='lightblue', edgecolor='blue', label='5-95% ppc', zorder=2, alpha=0.5)
    plt.title(title, fontsize=14)
    plt.legend(fontsize=10, frameon=False, loc='upper right')
    plt.ylabel('Voltage [mV]', fontsize=14); 
    plt.xlabel('Time [ms]', fontsize=14); 
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout();





def plot_corr(corr_vals, params_labels):
    fig = plt.figure(figsize=(5, 4))
    ax = fig.add_subplot(111)
    cmap = sns.diverging_palette(240, 10, sep=20, as_cmap=True)
    sns.heatmap(corr_vals, annot=True, robust=True, cmap=cmap, linewidths=.0, annot_kws={'size':8}, fmt=".2f", vmin=-1, vmax=1, ax=ax, xticklabels=params_labels, yticklabels=params_labels)

    for i in range(len(corr_vals)):
        for j in range(len(corr_vals)):
            text = ax.text(j + 0.5, i + 0.5, f"{corr_vals[i, j]:.2f}",
                           ha="center", va="center", color="black", fontsize=8)

    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=8)
    ax.tick_params(labelsize=12)

    

def plot_posterior_multimodal(my_var_names, theta_true, prior_predictions, az_obj_posterior, title):

    n_chains = az_obj_posterior.dims['chain']

    fig, ax = plt.subplots(ncols=5, nrows=2, figsize=(15, 5))
    for iprm, prm in enumerate(my_var_names) :
        a = ax[iprm//5, iprm%5]
        a.set_xlabel(prm)
        a.axvline(theta_true[iprm], color='r', label='true', linestyle='--')
        sns.kdeplot(prior_predictions[prm], ax=a, color='lime', alpha=0.9,  lw=2, linestyle='-', label='prior')
        for ichain in range(n_chains):
            sns.kdeplot(az_obj_posterior[prm][ichain, :], ax=a, alpha=0.7,  color=colors_l[ichain], label='chaque posterior')
    #ax[0, 0].legend()
    my_axis(ax, my_var_names)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.suptitle(title, fontsize=18)  
    fig.tight_layout(rect=[0, 0, 1, 1]) 




def plot_posterior_stackedmultimodal(my_var_names, theta_true, prior_predictions, az_obj_posterior, chains_stacked, title):

    n_chains = az_obj_posterior.dims['chain']

    fig, ax = plt.subplots(ncols=5, nrows=2, figsize=(15, 5))
    for iprm, prm in enumerate(my_var_names) :
        a = ax[iprm//5, iprm%5]
        a.set_xlabel(prm)
        a.axvline(theta_true[iprm], color='r', label='true', linestyle='--')
        #sns.kdeplot(prior_predictions[prm], ax=a, color='lime', alpha=0.9,  lw=2, linestyle='-', label='prior')
        sns.kdeplot(chains_stacked[iprm], color='gold', ax=a, lw=2, label='stack posteior', shade=True, zorder=3)

        for ichain in range(n_chains):
            sns.kdeplot(az_obj_posterior[prm][ichain, :], ax=a, alpha=0.7,  color=colors_l[ichain], label='chaque posterior')
    my_axis(ax, my_var_names)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.suptitle(title, fontsize=18)  
    fig.tight_layout(rect=[0, 0, 1, 1]) 




def out_of_samples_ppc_vales(data, ERP_JAXOdeintSimuator, chains_, n_):
    
    dt = data['dt']
    ts = data['ts']
    ds = data['ds']
    nt_obs = data['nt_obs']
    x_init = data['x_init']
    ts_obs = data['ts_obs']
    xpy_obs = data['xpy_obs']
    obs_err= data['obs_err']
 
    params_map_=calcula_map(chains_)

    n_params=int(len(params_map_))

    x_map_=ERP_JAXOdeintSimuator(x_init, ts, params_map_[0:n_params])
    
    sample_indices_= np.random.randint(0, chains_.shape[1], size=n_)
    joint_sample_ = chains_[:, sample_indices_]

    ppc_ = []
    for i_sample in range(chains_.shape[1]) :
        fit = ERP_JAXOdeintSimuator(x_init, ts, chains_[:, i_sample])
        noise = np.random.normal(loc=0, scale=obs_err, size=fit.shape)
        ppc_.append(fit + noise) 
    ppc_ = np.array(ppc_)

    xpy_per5_=np.quantile(ppc_, 0.5, axis=0)
    xpy_per95_=np.quantile(ppc_, 0.95, axis=0)

    return joint_sample_, ppc_[::ds], xpy_per5_[::ds], xpy_per95_[::ds], x_map_[::ds]    





def plot_out_of_sample_ppc_values(data, ERP_JAXOdeintSimuator, joint_sample_pooled, xpy_per5_pooled, xpy_per95_pooled, x_map_pooled, n_, title):

    dt = data['dt']
    ts = data['ts']
    ds = data['ds']
    nt_obs = data['nt_obs']
    x_init = data['x_init']
    ts_obs = data['ts_obs']
    xpy_obs = data['xpy_obs']
    obs_err= data['obs_err']


    n_params=int(joint_sample_pooled.shape[0])


    plt.figure(figsize=(6, 4))
    plt.plot(ts_obs, xpy_obs ,'.-', color='r', lw=2, label='observation');
    for i in range(n_):
        x_ppc_pooled=ERP_JAXOdeintSimuator(x_init, ts, joint_sample_pooled[:,i][0:n_params])[::ds]
        plt.plot(ts_obs, x_ppc_pooled, color='blue', lw=1, alpha=0.2)
    plt.plot(ts_obs, x_ppc_pooled, color='blue', lw=1, alpha=0.2, label='PPC')
    plt.fill_between(ts_obs, xpy_per5_pooled, xpy_per95_pooled, linewidth=4,facecolor='lightblue', edgecolor='lightblue', label='5-95% ppc', zorder=0)
    plt.plot(ts_obs, x_map_pooled, color='cyan', lw=3, alpha=0.2, label='MAP') 
    plt.title(title, fontsize=14)
    plt.legend(fontsize=10, frameon=False, loc='upper right')
    plt.ylabel('Voltage [mV]', fontsize=14); 
    plt.xlabel('Time [ms]', fontsize=14); 
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout();





def low_prob_sample(my_var_names, prior_predictions):
    
    prior_q = np.array([prior_predictions[prm] for prm in my_var_names]).T
    
    q_low_lim = np.quantile(prior_q, 0.0, axis=0)
    q_low = np.quantile(prior_q, 0.025, axis=0)
    q_high = np.quantile(prior_q, 0.975, axis=0)
    q_high_lim = np.quantile(prior_q, 1.0, axis=0)

    prob = np.array([q_low - q_low_lim, q_high_lim - q_high])
    prob = prob / prob.sum(axis=0) # Normalize to sum up to one
    
    n_params=int(len(my_var_names))

    low_prob_sample_vals = []
    for iprm in range(n_params) :
        low_prob_sample_vals.append(np.random.choice([np.random.uniform(q_low_lim[iprm], q_low[iprm]),
                                                 np.random.uniform(q_high[iprm], q_high_lim[iprm])], 
                                                 p=prob[:, iprm]))
        
    q_=[q_low_lim, q_low, q_high, q_high_lim]    
    return prior_q, low_prob_sample_vals, q_     



def plot_prior_tail(my_var_names, theta_true, prior_q, low_prob_sample_vals, q_):
    

    q_low_lim, q_low, q_high, q_high_lim=q_[0], q_[1], q_[2], q_[3], 

    
    fig, ax = plt.subplots(ncols=5, nrows=2, figsize=(15, 5))
    for iprm, prm in enumerate(my_var_names) :
        a = ax[iprm//5, iprm%5]
        sns.kdeplot(prior_q[:, iprm], color='lime', ax=ax[iprm//5, iprm%5], cut=0, label='prior')

        kde_x, kde_y = ax[iprm//5, iprm%5].lines[0].get_data()
        ax[iprm//5, iprm%5].fill_between(kde_x, kde_y, 
                                         where=((kde_x<=q_low[iprm]) & (kde_x>=q_low_lim[iprm])) | ((kde_x<=q_high_lim[iprm]) & (kde_x>=q_high[iprm])),
                                         color='cyan', alpha=0.7)

        ylim = ax[iprm//5, iprm%5].get_ylim()[1]
        ax[iprm//5, iprm%5].annotate('', xy=(low_prob_sample_vals[iprm], 0), 
                                     xytext=(low_prob_sample_vals[iprm], 0.5*ylim),
                                     horizontalalignment="center",
                                     arrowprops=dict(arrowstyle='->',lw=2, color='y'))
        ax[iprm//5, iprm%5].scatter(low_prob_sample_vals[iprm], 0.52*ylim, color='orange', s=50, label='init sample')
        a.axvline(theta_true[iprm], color='r', label='true', linestyle='--')

        if iprm % 5 == 0 or iprm % 5 == 4: 
            a.set_ylabel('Density') 
        else:
            a.set_ylabel('')
    my_axis(ax, my_var_names)           
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.suptitle("Initial values from the tail of prior", fontsize=18)  
    fig.tight_layout(rect=[0, 0, 1, 1])  

