import pickle

import networkx as nx
import matplotlib.pyplot as plt

from modules.grc_graph import GRCGraph

import pandas as pd

import datetime as dt

import numpy as np

from common.paths import File, Folder

# Get Number of cases DataFrame

dfc = pd.read_csv(File.input_matrix_of_weekly_cases, index_col=0)
dfc.columns = [int(wn) for wn in dfc.columns]

# Create Graph

grc_to_neighbours = GRCGraph.get_grc_to_neighbours(File.grc_neighbours_json)
G = GRCGraph.create_graph_from_neighbours(grc_to_neighbours_dictionary=grc_to_neighbours)

nx.draw(G, with_labels=True)
plt.show()


# drop data for locations not in nodes

dfc = dfc[dfc.index.isin(G.nodes())]


# reorder data based on node order
# need sorted(C.nodes()) because DGL will reassign node ordering as such
dfc = dfc.loc[sorted(G.nodes())]

# normalize values to [0,1]
dfc = dfc / dfc.values.max(axis=1, keepdims=True)
dfc.fillna(0.0, inplace=True) # some GRCs have 0 cases


# make C a directed graph
G = G.to_directed()



# Create Input Matrix

n_lags = 10
start_week = min(dfc.columns) + n_lags
end_week = max(dfc.columns)

# iterate over weeks and create graph with lagged node labels for each week
for week_number in range(start_week, end_week):

    if week_number not in dfc.columns:
        continue


    # get data in lag period
    start_lag = week_number - n_lags
    lag_weeks = dfc.columns[(dfc.columns < week_number) & (dfc.columns >= start_lag)]

    if len(lag_weeks) != 10:
        continue


    # create feature and response arrays
    confirmed = np.reshape(dfc[lag_weeks].values, (-1, n_lags, 1))

    #deaths = np.reshape(dfd[lag_dates].values, (-1, n_lags, 1))

    deaths = np.zeros(shape=(confirmed.shape[0], n_lags, 1))

    features = np.concatenate((confirmed, deaths), axis=2)

    #features = confirmed
    #targets = np.stack((dfc[date].values)).T

    targets = np.stack( (dfc[week_number].values, np.zeros(shape=confirmed.shape[0])) ).T

    # save feature and response arrays with original graph
    with open(Folder.weeks_folder + f'{str(week_number)}.pkl', 'wb') as f:
        pickle.dump((G, features, targets), f)

