import time

import frd.m04_save_data as save_data
import frd.m05_simulate as simulate
import frd.m06_analysis as analysis

if __name__ == '__main__':
    start = time.perf_counter()
    N_ITER = 100
    VERBOSE = False #whether to print info while running simulation
    SAVE = True #whether to save experiment data automatically before returning

    N_VOTERS = [3]
    N_CANDS = [5]
    N_ISSUES = [4] #Varying number of issues
    VOTERS_P = [0.5] #Bernoulli p for generating voter issue prefs
    CANDS_P = [0.5] #Bernoulli p for generating cand issue prefs
    APPROVAL_K = [3]
    APPROVAL_THRESH = [0.5]
    ELECTION_RULES = ['max_approval','borda', 'plurality', 'rav', 'max_agreement']
    N_REPS = [3]
    DEFAULT_STYLE = ['uniform']
    DEFAULT_PARAMS = [None]
    DELEGATION_STYLE = [None]
    DELEGATION_PARAMS = [None]

    #Set params for creating preference profiles
    profile_param_vals = {'n_voters':N_VOTERS,
                    'n_cands':N_CANDS,
                    'n_issues':N_ISSUES,
                    'voters_p':VOTERS_P,
                    'cands_p':CANDS_P,
                    'app_k':APPROVAL_K,
                    'app_thresh':APPROVAL_THRESH
                    }
    
    #Set params for electing reps
    election_param_vals = {'election_rules':ELECTION_RULES,
                    'n_reps':N_REPS}

    #Set params for delegative voting
    del_voting_param_vals = {'default_style':DEFAULT_STYLE,
                        'default_params':DEFAULT_PARAMS,
                        'delegation_style':DELEGATION_STYLE,
                        'delegation_params':DELEGATION_PARAMS}
    
    data, param_names, n_iter, experiment_params, filename = simulate.run_simulation(N_ITER, profile_param_vals, 
                                                      election_param_vals, 
                                                      del_voting_param_vals, 
                                                      verbose=VERBOSE,
                                                      save=SAVE)
    print('-----------------------------')
    end = time.perf_counter()
    print(f'Runtime: {end-start}')
    print(f'Runtime per iter: {(end-start)/N_ITER}')
    if SAVE: 
        print(f'Experiment data saved to: {filename}')
        data_loaded = save_data.unpickle_data(filename)
        #print(data_loaded)
        analysis.get_moments(filename, param_names, save=True)
    print('-----------------------------')







