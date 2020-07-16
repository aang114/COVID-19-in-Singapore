import dgl.function as fn
import torch.nn as nn
import torch.nn.functional as F

gcn_msg = fn.copy_src(src='h', out='m')
gcn_reduce = fn.sum(msg='m', out='h')


class GCNLSTM(nn.Module):
    def __init__(self, n_feats, seq_len):
        super(GCNLSTM, self).__init__()
        self.n_feats = n_feats
        self.seq_len = seq_len
        self.n_hidden = 10  # number of hidden states for LSTM cell
        self.n_layers = 3  # number of stacked LSTM layers

        self.lstm = nn.LSTM(input_size=n_feats,
                            hidden_size=self.n_hidden,
                            num_layers=self.n_layers,
                            batch_first=True,
                            dropout=0.3)

    def forward(self, g, feature):
        with g.local_scope():
            g.ndata['h'] = feature
            g.update_all(gcn_msg, gcn_reduce)
            h = g.ndata['h']
            return self.lstm(h)[0]


class GCNLinear(nn.Module):
  def __init__(self, in_feats, out_feats):
    super(GCNLinear, self).__init__()
    self.linear = nn.Linear(in_feats, out_feats)

  def forward(self, g, feature):
    with g.local_scope():
      g.ndata['h'] = feature
      g.update_all(gcn_msg, gcn_reduce)
      h = g.ndata['h']
      return self.linear(h)


class Net(nn.Module):
  def __init__(self):
    super(Net, self).__init__()

    self.layer1 = GCNLSTM(2, 10)
    self.dropout1 = nn.Dropout(0.3)
    self.layer2 = GCNLinear(100, 50)
    self.layer3 = GCNLinear(50, 2)

  def forward(self, g, features):
    batch_size, seq_len, n_feats = features.size()

    x = self.layer1(g, features)
    x = x.contiguous().view(batch_size, -1) # flatten
    x = F.relu(self.layer2(g, x))
    x = F.sigmoid(self.layer3(g, x))
    return x