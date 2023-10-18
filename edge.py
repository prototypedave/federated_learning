#!/usr/bin/env python3

""" Edge Server """
from model import AI_Model
from typing import List
from funcs import write_to_csv, generate_data
import sqlite3

class EdgeServer():
    # iniialize an instance of edge server
    def __init__(self):
        model = AI_Model()

        # create the baseline model to train vehicles
        self.baseline_model = model
        self.round = 0

        #self.update_baseline_model = False

    def train_test_model(self) -> None:
        train_lat, test_lat = self.baseline_model.train()
        filepath = "results_training/train_latency.csv"
        write_to_csv(filepath=filepath, x=self.round, y=train_lat)

        filepath = "results_training/test_latency.csv"
        write_to_csv(filepath=filepath, x=self.round, y=test_lat)
        self.round += 1

    def get_prediction(self, data) -> int:
        # train, save and return accuracy of the model
        self.train_test_model()

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

    def save_dataset(self, data) -> None:
        # saves each vehicle's dataset to the database
        conn = sqlite3.connect("learning.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO train_data (obstacles, weather, speed, distance, road_cond, time, risk_severity) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
        cur.execute("INSERT INTO test_data (obstacles, weather, speed, distance, road_cond, time, risk_severity) VALUES (?, ?, ?, ?, ?, ?, ?)", data)

        # Commit the changes
        conn.commit()

        # Close the connection
        conn.close()


if __name__ == "__main__":
    model = EdgeServer()
    for i in range(100):
        data = generate_data()
        model.save_dataset(data)
        new_data = data[:6]

        acc = model.get_prediction(new_data)
        
        