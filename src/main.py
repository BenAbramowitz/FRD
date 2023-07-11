import time
import numpy as np
import json
from pathlib import Path

import frd.m04_save_data as save_data
import frd.m05_simulate as simulate
import frd.m06_analysis as analysis

'''
NOTE: Currently, you want to vary only one independent variable per experiment if multiple rules are being compared. This makes life easier when it comes to plotting. More generally, you want to vary only one variable to place on the x-axis of the plot, and optionally one more variable (e.g. election rules) to plot multiple lines on a line plot.
'''

if __name__ == '__main__':
    p = Path(__file__).with_name('config.json')
    with p.open('r') as f:
        experiments = json.load(f)
        f.close()

    for e in experiments.keys(): #run all experiments
        print('-----------------------------')
        experiment_params = experiments[e]
        n_iter = experiment_params["n_iter"]
        save = experiment_params["save"]
        timer = experiment_params["timer"]
        seed = experiment_params["seed"]
        profile_param_vals = experiment_params["profile_param_vals"]
        election_param_vals = experiment_params["election_param_vals"]
        del_voting_param_vals = experiment_params["del_voting_param_vals"]
    
        if timer:
            start = time.perf_counter()

        np.random.seed(seed)
        data, param_names, n_iter, experiment_params, filename = simulate.sim_parallel(n_iter, profile_param_vals, election_param_vals, del_voting_param_vals, save=save)
        if save:
            data_loaded = save_data.unpickle_data(filename)
            print(f'Experiment data saved to: {filename}')
            analysis.get_moments(filename, param_names, save=True)
            print('Moments computed and saved')
        
        end = time.perf_counter()
        print(f'Runtime: {end-start}')
        print(f'Runtime per iter: {(end-start)/n_iter}')







