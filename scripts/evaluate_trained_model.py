import pandas as pd

import datetime as dt

from sklearn.metrics import r2_score

from sklearn.linear_model import LinearRegression

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pickle
import torch as th
import dgl
import json

from common.paths import File, Folder
from common.plot_type import PlotType

from modules.grc_graph import GRCGraph


def get_dfc():
    # Get Number of Cases DataFrame
    dfc = pd.read_csv(File.input_matrix, index_col=0)
    dfc.columns = pd.to_datetime(dfc.columns)

    # Create Graph
    grc_to_neighbours = GRCGraph.get_grc_to_neighbours(File.grc_neighbours_json)
    G = GRCGraph.create_graph_from_neighbours(grc_to_neighbours_dictionary=grc_to_neighbours)

    # drop data for locations not in nodes
    dfc = dfc[dfc.index.isin(G.nodes())]

    # reorder data based on node order
    # need sorted(C.nodes()) because DGL will reassign node ordering as such
    dfc = dfc.loc[sorted(G.nodes())]

    return dfc

def load_data(file):
    with open(f'../graph files/{file}', 'rb') as f:
        C, features, targets = pickle.load(f)
        features = th.FloatTensor(features)
        targets = th.FloatTensor(targets)
        g = dgl.DGLGraph()
        g.from_networkx(C)
        return g, features, targets


def get_denormalization_vector(df):

    return df.values.max(axis=1, keepdims=True).flatten()


def get_y_true_and_y_pred(files, neural_net, grc_row_number, denormalization_vector):

    y_true = []
    y_pred = []

    dates = []

    for file in files:
        date = dt.datetime.strptime(file[:-4], '%Y-%m-%d')
        dates.append(date)

        g, features, targets = load_data(file)
        targets = targets.numpy()[:, 0]
        preds = neural_net(g, features).data.numpy()[:, 0]

        if denormalization_vector is not None:
            targets = targets * denormalization_vector
            preds = preds * denormalization_vector

        if grc_row_number is not None:
            targets = targets[grc_row_number]
            preds = preds[grc_row_number]

            y_pred.append(preds.tolist())
            y_true.append(targets.tolist())

        else:
            y_pred.extend(preds.tolist())
            y_true.extend(targets.tolist())


    y_pred = np.reshape(np.array(y_pred), (len(y_pred), 1))
    y_true = np.reshape(np.array(y_true), (len(y_true), 1))

    return y_true, y_pred, dates


# Get Prediction vs Ground Truth R^2 value and Slope
def plot_graph(plot_type, y_true, y_pred, dates, graph_plot_directory):


    if plot_type == PlotType.TrainedModel.ground_truth_versus_prediction:

        plt.scatter(y_true, y_pred)
        plt.xlabel('Ground Truth')
        plt.ylabel('Prediction')

        title = 'Error 404'
        if graph_plot_directory == File.training_accuracy_png:
            title = 'Training Cases (Ground Truth vs Prediction)'
        elif graph_plot_directory == File.testing_accuracy_png:
            title = 'Testing Cases (Ground Truth vs Prediction)'

        plt.title(title)

        plt.savefig(graph_plot_directory)
        plt.clf()

    elif plot_type == PlotType.TrainedModel.date_versus_ground_truth_and_prediction_for_training_and_testing_dataset:

        training_y_true = y_true[0]
        testing_y_true = y_true[1]

        training_y_pred = y_pred[0]
        testing_y_pred = y_pred[1]

        training_dates = dates[0]
        testing_dates = dates[1]

        first_plot = plt.subplot(121)
        first_plot.scatter(training_dates, training_y_true, label='Ground Truth')
        first_plot.scatter(training_dates, training_y_pred, label='Prediction')
        first_plot.set_xlabel('Dates')
        first_plot.set_ylabel('Number of Cases')
        first_plot.legend(['Ground Truth', 'Prediction'])
        first_plot.set_ylim(bottom=0)
        first_title = 'Training Plot for {}'.format(grc_name)
        first_plot.set_title(first_title)
        first_ax = first_plot.axes
        first_ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        first_ax.xaxis.set_tick_params(rotation=90, labelsize=7)

        second_plot = plt.subplot(122)
        second_plot.scatter(testing_dates, testing_y_true, label='Ground Truth')
        second_plot.scatter(testing_dates, testing_y_pred, label='Prediction')
        second_plot.set_xlabel('Dates')
        second_plot.set_ylabel('Number of Cases')
        second_plot.legend(['Ground Truth', 'Prediction'])
        #second_plot.xticks(rotation=90)
        second_plot.set_ylim(bottom=0)
        second_title = 'Testing Plot for {}'.format(grc_name)
        second_plot.set_title(second_title)
        second_ax = second_plot.axes
        second_ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        second_ax.xaxis.set_tick_params(rotation=90, labelsize=7)

        plt.tight_layout()



        plt.savefig(graph_plot_directory)
        plt.clf()


    else:
        raise ValueError('plot_type Not Found!!')



def get_slope(x, y):
    reg = LinearRegression()
    reg.fit(x, y)

    slope = reg.coef_

    if slope.shape == (1, 1):
        slope_number = slope[0][0]
    else:
        raise ValueError("Slope's Shape is not (1,1)!")

    return slope_number


def get_r2_score(x, y):
    reg = LinearRegression()
    reg.fit(x, y)

    return reg.score(x, y)


with open(File.trained_model, 'rb') as f:
    net = pickle.load(file=f)

with open(File.train_files, 'rb') as f:
    train_files = pickle.load(file=f)

with open(File.test_files, 'rb') as f:
    test_files = pickle.load(file=f)

training_y_true, training_y_pred, _ = get_y_true_and_y_pred(files=train_files, neural_net=net, grc_row_number=None, denormalization_vector=None)
training_slope = get_slope(training_y_true, training_y_pred)
training_r2_score = get_r2_score(training_y_true, training_y_pred)

testing_y_pred, testing_y_true, _ = get_y_true_and_y_pred(files=test_files, neural_net=net, grc_row_number=None, denormalization_vector=None)
testing_slope = get_slope(testing_y_true, testing_y_pred)
testing_r2_score = get_r2_score(testing_y_true, testing_y_pred)

with open(File.model_accuracy_json, 'w') as f:

    dic = {'training_r2_score' : training_r2_score,
           'training_slope' : training_slope,
           'testing_r2_score' : testing_r2_score,
           'testing_slope' : testing_slope
           }

    json.dump(obj=dic, fp=f)


dfc = get_dfc()
denorm_vector = get_denormalization_vector(df=dfc)

training_y_true, training_y_pred, _ = get_y_true_and_y_pred(files=train_files, neural_net=net, grc_row_number=None, denormalization_vector=denorm_vector)

plot_graph(plot_type=PlotType.TrainedModel.ground_truth_versus_prediction,
           y_true=training_y_true,
           y_pred=training_y_pred,
           dates=None,
           graph_plot_directory=File.training_accuracy_png)

testing_y_true, testing_y_pred, _ = get_y_true_and_y_pred(files=test_files, neural_net=net, grc_row_number=None, denormalization_vector=denorm_vector)

plot_graph(plot_type=PlotType.TrainedModel.ground_truth_versus_prediction,
           y_true=testing_y_true,
           y_pred=testing_y_pred,
           dates=None,
           graph_plot_directory=File.testing_accuracy_png)



for row_number, grc_name in enumerate(dfc.index):

    training_y_true, training_y_pred, training_dates = get_y_true_and_y_pred(files=train_files, neural_net=net, grc_row_number=row_number, denormalization_vector=denorm_vector)

    testing_y_true, testing_y_pred, testing_dates = get_y_true_and_y_pred(files=test_files, neural_net=net,
                                                                             grc_row_number=row_number,
                                                                             denormalization_vector=denorm_vector)


    plot_graph(plot_type=PlotType.TrainedModel.date_versus_ground_truth_and_prediction_for_training_and_testing_dataset,
               y_true=(training_y_true, testing_y_true),
               y_pred=(training_y_pred, testing_y_pred),
               dates=(training_dates, testing_dates),
               graph_plot_directory=Folder.grc_accuracy_folder + '{}.png'.format(grc_name))