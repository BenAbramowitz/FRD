import logging
import time
import numpy as np
import json
from pathlib import Path
import os


import frd.m04_save_data as save_data
import frd.m05_simulate as simulate
import frd.m06_analysis as analysis
import frd.m07_plot as plot



'''
NOTE: Currently, you want to vary only one independent variable per experiment if multiple rules are being compared. This makes life easier when it comes to plotting. More generally, you want to vary only one variable to place on the x-axis of the plot, and optionally one more variable (e.g. election rules) to plot multiple lines on that line plot.
'''


def main():
    EXPERIMENTS = [] #Set which experiments to run. Runs all if list is empty
    N_ITER = 1000
    save=True
    show=False
    data_dir='./data/'

    p = Path(__file__).with_name('config.json')
    with p.open('r') as f:
        experiments = json.load(f)
        f.close()

    np.random.seed(1)

    for experiment_name in experiments.keys():
        if EXPERIMENTS and experiment_name not in EXPERIMENTS: continue #which experiments to run
        print('Starting Experiment '+str(experiment_name) +' running '+str(N_ITER) +' iterations')
        logging.info('')
        logging.info('Starting Experiment '+str(experiment_name) +' running '+str(N_ITER) +' iterations')
        #unpack experiment parameters
        experiment_params = experiments[experiment_name]
        profile_param_vals = experiment_params["profile_param_vals"]
        election_param_vals = experiment_params["election_param_vals"]
        del_voting_param_vals = experiment_params["del_voting_param_vals"]
    
        start = time.perf_counter()

        #run simulation for this experiment
        _, param_names, n_iter, experiment_params, filename = simulate.sim_parallel(N_ITER, 
        profile_param_vals, election_param_vals, del_voting_param_vals, save=save, experiment_name = experiment_name,data_dir=data_dir)

        #save data and analysis (i.e. moments) and generate plots
        if save == True:
            logging.info('Experiment data saved to '+str(filename)+' using pickle')
            _, momentsfile = analysis.get_moments(filename, param_names, save=True, data_dir=data_dir)
            logging.info('Moments computed and saved as csv')
            plot.plot_moments(momentsfile, y_var='mean', save=True, show=show, data_dir=data_dir) #will generate one plot for each independent variable, up to two
            logging.info('Plots created for mean agreement')
        
        #Report runtime
        end = time.perf_counter()
        logging.info(f'Total runtime: {end-start}')
        logging.info(f'Avg runtime per iteration: {(end-start)/n_iter}')

    logging.info('Done')



if __name__ == '__main__':
    open('frd.log', 'w').close() #hack because filemode='w' was corrupting the log file for unknown reasons
    logging.basicConfig(filename='frd.log', encoding='UTF-8', format='%(asctime)s %(levelname)s | %(module)s | %(funcName)s | %(message)s', level=logging.INFO)
    main()
    

    
