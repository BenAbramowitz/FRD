import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from os import listdir
from os.path import isfile, join

from . import m00_helper as helper

#Given a data file with experiments, we want to generate line plots
#Each line plot has an x_var, and y_var, and a l_var determining what each line represents (e.g. rules)
#pandas has good plotting tools, so might just use that for everything
#generalize to allow any l_var instead of just rules

def check_csv(filename):
    if not filename.endswith('.csv'):
        raise ValueError('compare_rules can only read in csv files to plot')

def label_compare_rules_plot(filename, x_var, y_var):
    prefix = helper.get_file_prefix(filename)
    path = Path("./data")
    datafile = str([f for f in listdir(path) if isfile(join(path, f)) and f[0:3] == prefix and 'moments' not in f])

    title = ""
    x_label, y_label = "", ""
    print(f'datafile: {datafile}')
    if "FRD" in datafile:
        title = "FRD: "
    elif "RD" in datafile:
        title = "RD: "

    if y_var == 'mean':
        y_label = "Mean Agreement"
    elif y_var == 'variance':
        y_label = "Agreement Variance"
    elif y_var == 'skew':
        y_label = "Agreement Skewness"
    elif y_var == "kurtosis":
        y_label = "Agreement Kurtosis"
    else:
        raise ValueError(f"Do not know how to use {y_var} in title of plot")
    
    title += y_label
    
    title += " vs "

    if x_var.lower() == 'n_voters':
        x_label = "Number of Voters"
    elif x_var.lower() == 'n_cands':
        x_label = "Number of Cands"
    elif x_var.lower() == 'n_issues':
        x_label = "Number of Issues"
    elif x_var.lower() == 'n_reps':
        x_label = "Committee Size"
    elif x_var.lower() == 'voters_p':
        x_label = "Voters' Bernoulli Parameter"
    elif x_var.lower() == 'cands_p':
        x_label = "Cands' Bernoulli Parameter"
    elif x_var.lower() == 'app_k':
        x_label = "Max Approvals Per Voter"
    elif x_var.lower() == "app_thresh":
        x_label = "Approval Threshold"
    elif x_var.lower() == "default_style":
        x_label = "Default Weighting"
    elif x_var.lower() == "default_params":
        x_label = "Default Parameter"
    elif x_var.lower() == "delegation_style":
        x_label = "Delegation Style"
    elif x_var.lower() == "delegation_params":
        x_label = "Delegation Parameter"

    title += x_label

    return title, x_label, y_label

def compare_rules(filename, x_var:str, y_var='mean', save=True, show=False, data_dir='./data/'):
    '''
    Takes in a dataframe of agreements and then plots agreement vs. x_var lines for each rule

    TODO
    ----------
    Change labels of election rules in the legend to title chase

    NOTES
    ------
    If the data set has more than one independent variable that was varied, this plot will not come out right.
    If plot exists with the same name it will get overwritten

    '''
    check_csv(filename)
    df = pd.read_csv(data_dir+filename)
    #Need to change title and axis labels
    p = sns.lineplot(data=df, x=x_var, y=y_var, hue='election_rules')
    title, xlabel, ylabel = label_compare_rules_plot(filename, x_var, y_var)
    p.legend(title='Election Rules')

    p.set(title=title, xlabel=xlabel, ylabel=ylabel)
    if save:
        prefix = helper.get_file_prefix(filename)
        fig = p.get_figure()
        fig.savefig('./plots/'+prefix+'_rules_vs_'+x_var)
    if show:
        plt.show()