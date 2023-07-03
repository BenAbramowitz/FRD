# FRD
README.md for Flexible Representative Democracy

This is the implementation and code used for our forthcoming SCW journal paper, which will also be available on arXiv. The code for our IJCAI 2019 paper differed slightly (been refactored).

For more information on Flexible Representative Democracy, please see our publications. Please cite these publications if you use this code in any academic capacity or are just feeling friendly.


## Setup / Installation
```bash pip install -r requirements.txt```

## Run Experiments
```[Stay Tuned]```

The generic experiment structure has 3 steps: Profile creation, election, and weighted (delegative) voting. Each of these has its own module (m01, m02, and m03).


## Project Organization
Code in /src, data in /data, plots in /plots

src contains /frd, the main package for running the simulations, /tests for testing the modules in /frd, and /experiments for running experiments to generate data and plots

The modules in frd are all py files, and the experiments are run from python files but the data is visualized/plotted in jupyter notebooks (ipynb)

Naming conventions for modules within each directory is that we try to keep them ordered so that mX... can only import mY... if Y < X. So m02_election_rules can import m01_profiles but not vice versa. This helps prevent any potential import cycles.


## Dev Notes / Implementation Details
- Currently ordinal prefs (orders, ordermaps) cannot be incomplete. This differs from older version. This is because these ordinal preferences are dicts where keys are voters and values are 1D numpy arrays of fixed length. Old version had dict of dicts, as in {v1 : {c1:0, c2:1}, v2: {c1:1, c2:0}}
- score_orders and score_ordermaps currently use nested for loops that are slow, but easy to read and debug. Can speed up with map or comprehensions later if needed.
- Currently stv/irv not implemented. Could use whalrus, but need to convert the profile order to a whalrus ballot . If we want to use whalrus for other rules in the future it will be more efficient to have this conversion be a method of the Profile object.
- Currently Chamberlain-Courant and k-Medians are not implemented either (both NP-Hard).
- Still have ordermaps implemented from earlier implementation but does not currently appear to be needed. Might be useful for implementing STV, but if not it can probably be removed.