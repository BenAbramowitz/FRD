import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from . import m00_helper as helper


#Given a data file with experiments, we want to generate line plots
#Each line plot has an x_var, and y_var, and a l_var determining what each line represents (e.g. rules)
#pandas has good plotting tools, so might just use that for everything
#generalize to allow any l_var instead of just rules

def compare_rules(filename, x_var:str, y_var='mean', save=True, show=False, data_dir='./data/'):
    '''
    Takes in a dataframe of agreements and then plots agreement vs. x_var lines for each rule

    TODO
    ----------
    Change title and axis labels, and make sure y-axis goes from 0.0-1.0

    NOTES
    ------
    If the data set has more than one independent variable that was varied, this plot will not come out right.
    If plot exists with the same name it will get overwritten

    '''
    if not filename.endswith('.csv'):
        raise ValueError('compare_rules can only read in csv files to plot')
    df = pd.read_csv(data_dir+filename)
    #Need to change title and axis labels
    p = sns.lineplot(data=df, x=x_var, y=y_var, hue='election_rules')
    if save:
        prefix = helper.get_file_prefix(filename)
        fig = p.get_figure()
        fig.savefig('./plots/'+prefix+'_rules_vs_'+x_var)
    if show:
        plt.show()