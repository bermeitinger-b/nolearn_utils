import pickle

import numpy as np


class EarlyStopping(object):
    """From https://github.com/dnouri/kfkd-tutorial"""

    def __init__(self, patience=50):
        self.patience = patience
        self.best_valid = np.inf
        self.best_valid_epoch = 0
        self.best_params = None

    def __call__(self, nn, train_history):
        current_valid = train_history[-1]['valid_loss']
        current_train = train_history[-1]['train_loss']
        current_epoch = train_history[-1]['epoch']

        # Ignore if training loss is greater than valid loss
        if current_train > current_valid:
            return

        if current_valid < self.best_valid:
            self.best_valid = current_valid
            self.best_valid_epoch = current_epoch
            self.best_params = nn.get_all_params_values()
        elif self.best_valid_epoch + self.patience <= current_epoch:
            print('Early stopping.')
            print('Best valid loss was {:.6f} at epoch {}.'.format(
                self.best_valid, self.best_valid_epoch))
            nn.load_params_from(self.best_params)
            raise StopIteration()


class StepDecay(object):
    """From https://github.com/dnouri/kfkd-tutorial"""

    def __init__(self, name, start=0.03, stop=0.001, delay=0):
        self.name = name
        self.delay = delay
        self.start, self.stop = start, stop
        self.ls = None

    def __call__(self, net, train_history):
        if self.ls is None:
            self.ls = np.linspace(self.start, self.stop,
                                  net.max_epochs - self.delay)

        epoch = train_history[-1]['epoch'] - self.delay
        if epoch >= 0:
            new_value = float32(self.ls[epoch - 1])
            getattr(net, self.name).set_value(new_value)


class SaveTrainingHistory(object):
    def __init__(self, path, verbose=0):
        self.path = path
        self.verbose = verbose

    def __call__(self, nn, train_history):
        with open(self.path, 'wb') as f:
            pickle.dump(train_history, f, -1)


def float32(x):
    return np.cast['float32'](x)
