import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import pickle
import os

import torch as th
import dgl

from modules.gnn_model import *

from common.paths import File

def load_data(file):
    with open(f'../graph files/{file}', 'rb') as f:
        C, features, targets = pickle.load(f)
        features = th.FloatTensor(features)
        targets = th.FloatTensor(targets)
        g = dgl.DGLGraph()
        g.from_networkx(C)
        return g, features, targets


th.manual_seed(0)
net = Net()
print(net)


# Train Model


train_files = []
test_files = []

for file in os.listdir('../graph files/'):
    date = dt.datetime.strptime(file[:-4], '%Y-%m-%d')
    if date < dt.datetime.strptime('2020-06-26', '%Y-%m-%d'):
        train_files.append(file)
    else:
        test_files.append(file)



optimizer = th.optim.Adam(net.parameters(), lr=1e-3)

n_epochs = 500

train_loss = []
test_loss = []


for epoch in range(n_epochs):
    train_loss_epoch = []
    test_loss_epoch = []

    for file in train_files:

        g, features, targets = load_data(file)

        net.train()

        pred = net(g, features)
        loss = F.mse_loss(pred, targets)
        train_loss_epoch.append(loss.item())

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()


    for file in test_files:

        g, features, targets = load_data(file)
        pred = net(g, features)
        loss = F.mse_loss(pred, targets)
        test_loss_epoch.append(loss.item())

    train_loss.append(np.mean(train_loss_epoch))
    test_loss.append(np.mean(test_loss_epoch))

    if epoch % 50 == 0:
        print(f'Epoch: {epoch}, Train Loss: {train_loss[epoch]}, Test Loss: {test_loss[epoch]}')




# Show Loss vs Epoch Plot
plt.plot(train_loss)
plt.plot(test_loss)
plt.title('Loss vs. Epochs')
plt.ylim((0,0.6))

plt.savefig(File.loss_vs_epoch_png)
#plt.show()

# Save Model and Train and Test Files

with open(File.trained_model, 'wb') as f:
    pickle.dump(obj=net, file=f)

with open(File.train_files, 'wb') as f:
    pickle.dump(obj=train_files, file=f)

with open(File.test_files, 'wb') as f:
    pickle.dump(obj=test_files, file=f)



# Forecast

def one_day_forecast(g, features):
    pred = net(g, features)
    new_features = th.zeros(features.size())
    new_features[:, 0:9, :] = features[:, 1:10, :]
    new_features[:, 9, :] = pred
    return pred, new_features

def several_day_forecast(g, features, n_days):
    new_features = features
    for i in range(n_days):
        pred, new_features = one_day_forecast(g, new_features)
    return pred, new_features


#g, features, targets = load_data('2020-06-26.pkl')
#pred, new_features = several_day_forecast(g, features, 7)

#g, true_features, targets = load_data('2020-07-03.pkl')

# look at illinois as example (14 is index of illinois)
#plt.plot(new_features[14, :, 0].detach().numpy())
#plt.plot(true_features[14, :, 0].detach().numpy())
#plt.title('Illinois Confirmed Cases')
#plt.ylim((0.6, 1))
#plt.show()

# sqrt(test_loss[499])


