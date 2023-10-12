#!/usr/bin/env python3

""" Edge Server """
from model import AI_Model

class EdgeServer():
    # iniialize an instance of edge server
    def __init__(self):
        model = AI_Model()

        # create the baseline model to train vehicles
        self.baseline_model = model

        #self.update_baseline_model = False

    def train_each_vehicle(self, data) -> int:
        # train, save and return accuracy of the model
        model = self.baseline_model

        prediction = model.predict(data)
        
        if prediction is sum(data):
            accurate = 1
        else:
            accurate = 0
        
        return accurate
    
    def learning_summary(self, num_vehicles, data):
        # Aggregates the learning summary of the model after each vehicle
        accuracy =  sum(data) / num_vehicles * 100

        
    def prediction(self, data):
        # Makes prediction on the improved model
        model = self.baseline_model
        prediction = model.predict(data)
        return prediction
    
    def update_baseline(self):
        # update the baseline
        pass
        