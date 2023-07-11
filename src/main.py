import time
import numpy as np
import json
from pathlib import Path

import frd.m04_save_data as save_data
import frd.m05_simulate as simulate
import frd.m06_analysis as analysis

'''
NOTE: Currently, you want to vary only one independent variable per experiment if multiple rules are being compared. This makes life easier when it comes to plotting. More generally, you want to vary only one variable to place on the x-axis of the plot, and optionally one more variable (e.g. election rules) to plot multiple lines on that line plot.

election rules: ["max_approval","borda","plurality","rav", "max_agreement", "random_winners"]
'''

EXPERIMENTS = ['1a', '1a_polarized', '1a_similar', '1b', '1b_polarized', '1b_similar', '1c', '1c_polarized', '1c_similar']

if __name__ == '__main__':
    p = Path(__file__).with_name('config.json')
    with p.open('r') as f:
        experiments = json.load(f)
        f.close()

    save=True
    timer=True

    for experiment_name in experiments.keys(): #run all experiments
        if experiment_name not in EXPERIMENTS: continue
        print('-----------------------------')
        print('Experiment', experiment_name)
        experiment_params = experiments[experiment_name]
        n_iter = experiment_params["n_iter"]
        seed = experiment_params.get("seed",None)
        profile_param_vals = experiment_params["profile_param_vals"]
        election_param_vals = experiment_params["election_param_vals"]
        del_voting_param_vals = experiment_params["del_voting_param_vals"]
    
        if timer:
            start = time.perf_counter()

        np.random.seed(seed)
        data, param_names, n_iter, experiment_params, filename = simulate.sim_parallel(n_iter, profile_param_vals, election_param_vals, del_voting_param_vals, save=save, experiment_name = experiment_name)
        if save:
            print(f'Experiment {experiment_name} data saved to: {filename} using pickle')
            data_loaded = save_data.unpickle_data(filename)
            analysis.get_moments(filename, param_names, save=True)
            print('Moments computed and saved as csv')
        
        end = time.perf_counter()
        print(f'Total runtime: {end-start}')
        print(f'Avg runtime per iteration: {(end-start)/n_iter}')







