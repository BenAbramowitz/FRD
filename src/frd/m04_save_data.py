import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import pandas as pd
import pickle
import numpy as np

def number_experiment():
    '''
    read in all the files in data folder prefixed by a number, and find the largest (or 0 if empty), then add one.
    The goal is to give all experiments a unique ID. Assuming < 1000 experiments.
    '''
    #
    path = Path("./data")
    datafiles = [f for f in listdir(path) if isfile(join(path, f))]
    n = 0
    for f in datafiles:
        prefix = ""
        for char in f:
            if char.isdigit():
                prefix += char
            else:
                break
        n = max(int(prefix), n)
    return n+1

def name_experiment(experiment_params:dict):
    '''
    '''
    n = number_experiment() #get number n of experiment to use as prefix
    if n < 10: name = '00'+str(n)
    elif n < 100: name = '0'+str(n)
    else: name = +str(n)

    if len(experiment_params['n_voters']) > 1: name += '_varyV'
    else: name += '_'+str(experiment_params['n_voters'][0])+'V'

    if len(experiment_params['n_cands']) > 1: name += '_varyC'
    else: name += '_'+str(experiment_params['n_cands'][0])+'C'

    if len(experiment_params['n_issues']) > 1: name += '_varyS'
    else: name += '_'+str(experiment_params['n_issues'][0])+'S'

    if len(experiment_params['voters_p']) > 1: name += '_varyVP'
    else: name += '_'+str(int(experiment_params['voters_p'][0]*100))+'VP'

    if len(experiment_params['cands_p']) > 1: name += '_varyCP'
    else: name += '_'+str(int(experiment_params['cands_p'][0]*100))+'CP'

    if len(experiment_params['app_k']) > 1: name += '_varyAPPK'
    else: name += '_'+str(experiment_params['app_k'][0])+'APPK'

    if len(experiment_params['app_thresh']) > 1: name += '_varyAPPT'
    else: name += '_'+str(int(experiment_params['app_thresh'][0]*100))+'APPT'

    if len(experiment_params['election_rules']) > 1: name += '_varyR'
    else: name += '_'+experiment_params['election_rules']

    if len(experiment_params['n_reps']) > 1: name += '_varyCS'
    else: name += '_'+str(experiment_params['n_reps'][0])+'CS'

    if len(experiment_params['default_style']) > 1: name += '_varyDEF'
    else: name += '_'+str(experiment_params['default_style'][0])+'DEF'

    if len(experiment_params['delegation_style']) > 1: name += '_varyDEL_FRD'
    else: 
        if experiment_params['delegation_style'] != [None]:
            name += '_'+str(experiment_params['delegation_style'][0])+'DEL_FRD'
        else:
            name += '_RD'

    return name

def pickle_data(data:dict, experiment_params:dict, filename:str = None):
    '''
    Save experiment data (dict), creating a filename if not given.

    NOTES
    --------
    Currently, if a file exists this will overwrite the contents of that file.

    TO DO
    -------
    If filename already exists, then append the data
    '''

    if filename is None: 
        filename = name_experiment(experiment_params)
        # print(f'filename created: {filename}')

    # data['param_names'] = list(experiment_params.keys())
    with open('./data/'+filename, 'wb') as output_file:
        pickle.dump(data, output_file)

    return filename

def unpickle_data(filename):
    with open('./data/'+filename, 'rb') as input_file:
        data = pickle.load(input_file)
    return data

