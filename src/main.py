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
    N_ITER = 1
    profile_param_vals = {'n_voters':[3],
                    'n_cands':[3],
                    'n_issues':[4,10], #Varying number of issues
                    'voters_p':[0.5],
                    'cands_p':[0.5],
                    'approval_params':[(3, 0.5)]}
    election_param_vals = {'election_rules':['max_approval'],
                    'n_reps':[1]}
    del_voting_param_vals = {'default_style':['uniform'],
                        'default_params':[None],
                        'delegation_style':[None],
                        'delegation_params':[None]}
    
    data, experiment_params = simulate.run_simulation(N_ITER, profile_param_vals, election_param_vals, del_voting_param_vals)
    # print(data)
    # print(experiment_params)
    # filename = save_data.name_dataset(experiment_params)
    # save_data.save_raw(data, filename, filetype = 'pickle')




