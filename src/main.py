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

EXPERIMENTS = ['RD_reps','RD_cands'] #Set which experiments to run. Runs all if list is empty
N_ITER = 1

if __name__ == '__main__':
    p = Path(__file__).with_name('config.json')
    with p.open('r') as f:
        experiments = json.load(f)
        f.close()

    save=True
    show=False
    timer=True
    data_dir = './data/'
    
    np.random.seed(1)

    for experiment_name in experiments.keys():
        if EXPERIMENTS and experiment_name not in EXPERIMENTS: continue #which experiments to run
        print('-----------------------------')
        print('Experiment', experiment_name)
        print(f'Running {N_ITER} iterations')
        #unpack experiment parameters
        experiment_params = experiments[experiment_name]
        profile_param_vals = experiment_params["profile_param_vals"]
        election_param_vals = experiment_params["election_param_vals"]
        del_voting_param_vals = experiment_params["del_voting_param_vals"]
    
        if timer: start = time.perf_counter()

        #run simulation for this experiment
        data, param_names, n_iter, experiment_params, filename = simulate.sim_parallel(N_ITER, 
        profile_param_vals, election_param_vals, del_voting_param_vals, save=save, experiment_name = experiment_name,data_dir=data_dir)

        #save data and analysis (i.e. moments) and generate plots
        if save == True:
            print(f'Experiment data saved to: {filename} using pickle')
            _, momentsfile = analysis.get_moments(filename, param_names, save=True, data_dir=data_dir)
            print('Moments computed and saved as csv')
            plot.plot_moments(momentsfile, y_var='mean', save=True, show=show, data_dir=data_dir) #will generate one plot for each independent variable, up to two
            print('Plots created for mean agreement')
        
        #Report runtime
        if timer:
            end = time.perf_counter()
            print(f'Total runtime: {end-start}')
            print(f'Avg runtime per iteration: {(end-start)/n_iter}')

    #Create plots for all data in the data folder and save/show them
    # if save: plot.compare_all(data_dir='./data/', y_var='mean', save=True, show=False)


