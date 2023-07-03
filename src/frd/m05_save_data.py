import os
from pathlib import Path
import pandas as pd

def number_dataset():
    #read in all the files in data folder prefixed by a number, and find the largest (or 0 if empty), then add one
    path = Path("./data")
    pass

def name_dataset(experiment_params:dict):
    n = number_dataset() #get number of experiment to use as prefix
    #create filename based on n & which variables are varied & num_iter & date
    pass

def save_raw(data:dict, filename:str = None, filetype='pickle'):
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

