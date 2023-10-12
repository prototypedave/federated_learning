#!/usr/bin/env python3

""" Neural Network """

import torch, torch.nn as nn


# Define the neural network model
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(6, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, 256)
        self.fc3 = nn.Linear(256, 10)

    def forward(self, state):
        x = self.fc1(state)
        x = self.relu(x)

        x = self.fc2(x)
        x = self.relu(x)

        output = self.fc3(x)
        return output

