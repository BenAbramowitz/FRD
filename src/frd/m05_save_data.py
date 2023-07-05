import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import pandas as pd

def number_experiment():
    #read in all the files in data folder prefixed by a number, and find the largest (or 0 if empty), then add one
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

def name_experiment(data:dict):
    n = number_experiment() #get number n of experiment to use as prefix
    if n < 10: name = '00'+str(n)
    elif n < 100: name = '0'+str(n)
    else: name = +str(n)

    if len(data['n_voters']) > 1: name += '_varV'
    else: name += '_'+str(data['n_voters'][0])+'V'

    if len(data['n_cands']) > 1: name += '_varC'
    else: name += '_'+str(data['n_cands'][0])+'C'

    if len(data['n_issues']) > 1: name += '_varS'
    else: name += '_'+str(data['n_issues'][0])+'S'

    if len(data['voters_p']) > 1: name += '_varVP'
    else: name += '_'+str(int(data['voters_p'][0]*100))+'VP'

    if len(data['cands_p']) > 1: name += '_varCP'
    else: name += '_'+str(int(data['cands_p'][0]*100))+'CP'

    if len(data['app_k']) > 1: name += '_varAPPK'
    else: name += '_'+str(data['app_k'][0])+'APPK'

    if len(data['app_thresh']) > 1: name += '_varAPPT'
    else: name += '_'+str(int(data['app_thresh'][0]*100))+'APPT'

    if len(data['election_rules']) > 1: name += '_varR'
    else: name += '_'+data['election_rules']

    if len(data['n_reps']) > 1: name += '_varCS'
    else: name += '_'+str(data['n_reps'][0])+'CS'

    if len(data['default_style']) > 1: name += '_varDEF'
    else: name += '_'+str(data['default_style'][0])

    if len(data['delegation_style']) > 1: name += '_varDEL_FRD'
    else: 
        if data['delegation_style'] != [None]:
            name += '_'+str(data['delegation_style'][0])+'_FRD'
        else:
            name += '_RD'

    return name

def save_data(data:dict, experiment_params:dict, filename:str = None, filetype='pickle'):
    #if filename exists, then we'll append the data
    #if filename is None, we'll create a filename
    #if filename is not None but does not exist, we'll create a file with that name
    
    #convert the dict to a dataframe
    #if filetype == 'csv'
        #use dataframe.to_csv to write to file
    #if filetype == 'pickle'
        #use dataframe.to_pickle
    path = Path("./data")
    path = os.path.join(path, filename)
    # with open(path, 'w') as f:
    #     f.write('here')
    # f.close()
    pass

