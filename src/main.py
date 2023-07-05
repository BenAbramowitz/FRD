# import numpy as np
# import pandas as pd
# import pickle

import frd.m00_helper as helper
import frd.m01_profiles as profiles
import frd.m02_election_rules as rules
import frd.m03_delegative_voting as d_voting
import frd.m04_simulate as simulate
import frd.m05_save_data as save_data
import frd.m06_analysis as analysis

if __name__ == '__main__':
    N_ITER = 3

    #Set params for creating preference profiles
    N_VOTERS = [3]
    N_CANDS = [3]
    N_ISSUES = [4,10] #Varying number of issues
    VOTERS_P = [0.5]
    CANDS_P = [0.5]
    APPROVAL_K = [3]
    APPROVAL_THRESH = [0.5]
    profile_param_vals = {'n_voters':N_VOTERS,
                    'n_cands':N_CANDS,
                    'n_issues':N_ISSUES,
                    'voters_p':VOTERS_P,
                    'cands_p':CANDS_P,
                    'app_k':APPROVAL_K,
                    'app_thresh':APPROVAL_THRESH
                    }
    
    #Set params for electing reps
    ELECTION_RULES = ['max_approval','borda']
    N_REPS = [1]
    election_param_vals = {'election_rules':ELECTION_RULES,
                    'n_reps':N_REPS}

    #Set params for delegative voting
    DEFAULT_STYLE = ['uniform']
    DEFAULT_PARAMS = [None]
    DELEGATION_STYLE = [None]
    DELEGATION_PARAMS = [None]
    del_voting_param_vals = {'default_style':DEFAULT_STYLE,
                        'default_params':DEFAULT_PARAMS,
                        'delegation_style':DELEGATION_STYLE,
                        'delegation_params':DELEGATION_PARAMS}
    
    data, param_names, n_iter, experiment_params = simulate.run_simulation(N_ITER, profile_param_vals, 
                                                      election_param_vals, 
                                                      del_voting_param_vals, 
                                                      verbose=True,
                                                      save=True)
    print('-----------------------------')
    # print(f'data: {data}')
    # print(f'param_names: {param_names}')
    # print(f'experiment_params: {experiment_params}')
    # filename = save_data.name_dataset(experiment_params)
    # save_data.save_raw(data, filename, filetype = 'pickle')
    print('-----------------------------')
    print(save_data.number_experiment())
    print(save_data.name_experiment(experiment_params))




