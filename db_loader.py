#!/usr/bin/python3

""" DB Dataset Loader """

import sqlite3
import torch
from torch.utils.data import Dataset

class CustomDataset(Dataset):
    # initialize the class dataset
    def __init__(self, db_file, table_name):
        self.features, self.labels = self.load_data_from_db(db_file, table_name)

    # gets the the featres and labels of an individual vehicle and converts it to tensor
    def __getitem__(self, index):
        features = torch.tensor(self.features[index], dtype=torch.float32)
        label = torch.tensor(self.labels[index], dtype=torch.long)
        return features, label

    # returns the length of the features (by deault should be 6)
    def __len__(self):
        return len(self.features)

    # Fetches all the available dataset in the named db file and returns the eatures and labels
    def load_data_from_db(self, db_file, table_name):
        # Connect to the database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Fetch data from the table
        cursor.execute(f"SELECT obstacles, weather, speed, distance, road_cond, time, risk_severity FROM {table_name}")
        rows = cursor.fetchall()

        # Separate features and labels
        features = []
        labels = []
        for row in rows:
            features.append(row[:-1])  # Exclude the last column (risk_severity)
            labels.append(row[-1])  # Extract the risk_severity

        # Close the database connection
        conn.close()

        return features, labels