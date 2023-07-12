import time
import numpy as np
import json
from pathlib import Path

import frd.m04_save_data as save_data
import frd.m05_simulate as simulate
import frd.m06_analysis as analysis
import frd.m07_plot as plot

'''
NOTE: Currently, you want to vary only one independent variable per experiment if multiple rules are being compared. This makes life easier when it comes to plotting. More generally, you want to vary only one variable to place on the x-axis of the plot, and optionally one more variable (e.g. election rules) to plot multiple lines on that line plot.
'''

EXPERIMENTS = ['RD_cands_p','RD_cands_p_biased','1a', '1b', '1c', '1a_polarized', '1a_similar', '1b_polarized', '1b_similar', '1c_polarized', '1c_similar'] #which experiments to run

if __name__ == '__main__':
    p = Path(__file__).with_name('config.json')
    with p.open('r') as f:
        experiments = json.load(f)
        f.close()

    save=True
    timer=True
    n_iter = 1
    np.random.seed(1)

    for experiment_name in experiments.keys():
        if experiment_name not in EXPERIMENTS: continue #which experiments to run
        print('-----------------------------')
        print('Experiment', experiment_name)
        #unpack experiment parameters
        experiment_params = experiments[experiment_name]
        profile_param_vals = experiment_params["profile_param_vals"]
        election_param_vals = experiment_params["election_param_vals"]
        del_voting_param_vals = experiment_params["del_voting_param_vals"]
    
        if timer: start = time.perf_counter()

        #run simulation for this experiment
        data, param_names, n_iter, experiment_params, filename = simulate.sim_parallel(n_iter, profile_param_vals, election_param_vals, del_voting_param_vals, save=save, experiment_name = experiment_name)

        #save data and anlysis (i.e. moments)
        if save:
            print(f'Experiment data saved to: {filename} using pickle')
            data_loaded = save_data.unpickle_data(filename)
            analysis.get_moments(filename, param_names, save=True)
            print('Moments computed and saved as csv')
        
        #Report runtime
        if timer:
            end = time.perf_counter()
            print(f'Total runtime: {end-start}')
            print(f'Avg runtime per iteration: {(end-start)/n_iter}')

    #Create plots for all data in the data folder and save/show them
    if save: plot.compare_all(data_dir='./data/', y_var='mean', save=True, show=False)


