import numpy as np
import pandas as pd
from pathlib import Path
import os
from os.path import join
# import pickle
from scipy import stats

import frd.m04_save_data as save_data

def four_moments(array):
    '''given data dict, get the mean and variance for each run. Write results to csv file.'''
    mean = np.mean(array)
    variance = np.var(array)
    skew = stats.skew(array)
    kurtosis = stats.kurtosis(array)
    return [mean, variance, skew, kurtosis]

def get_moments(filename, param_names, save=True):
    '''
    Load data from file, compute moments for each parameterization in that experiment, then save analysis as csv
    '''
    data = save_data.unpickle_data(filename)
    path = Path("./data")

    analyzed = [list(params) + four_moments(agreements) for params, agreements in data.items()]
    df = pd.DataFrame(analyzed, columns = param_names+['mean','variance','skew','kurtosis'])
    if save == True: 
        filename += '_moments.csv'
        df.to_csv(os.path.join(path, filename))