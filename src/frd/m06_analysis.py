import numpy as np
import pandas as pd
from pathlib import Path
import os
# from os.path import join
# import pickle
from scipy import stats

import frd.m04_save_data as save_data

def four_moments(array):
    '''
    Given data dict, return the mean, variance, skew, and kurtosis for ethe agreements data for each parameterization.
    '''
    mean = np.mean(array)
    variance = np.var(array)
    skew = stats.skew(array)
    kurtosis = stats.kurtosis(array)
    return [mean, variance, skew, kurtosis]

def get_moments(filename, param_names, save=True, data_dir='../data'):
    '''
    Load data from file, compute moments for each parameterization in that experiment, then save analysis as csv

    RETURNS
    -------
    df (pd.DataFrame): has col for each parameter val and columns for mean, variance, skew, and kurtosis of the agreements data, row for each parameterization
    '''
    data = save_data.unpickle_data(filename, data_dir=data_dir)
    path = Path(data_dir)

    analyzed = [list(params) + four_moments(agreements) for params, agreements in data.items()]
    df = pd.DataFrame(analyzed, columns = param_names+['mean','variance','skew','kurtosis'])
    if save == True: 
        filename = filename.partition('_data')[0]+'_moments.csv'
        df.to_csv(os.path.join(path, filename))
    return df, filename