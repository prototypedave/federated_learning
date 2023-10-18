#!/usr/bin/python3

"""  AI_Model """

from neural import NeuralNetwork
from db_loader import CustomDataset
from torch.utils.data import DataLoader
from funcs import generate_data, write_to_csv
import os, sqlite3, torch
import torch.optim as optim, torch.nn as nn
import time

# Load cuda if present
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
num_epochs = 1000

# Define the model
class AI_Model():
    def __init__(self) -> None:
        self.model: NeuralNetwork = NeuralNetwork()
        self.iterate = 0
    

        # load previously pre trained model
        if os.path.exists("federated_model.pth"):    
            self.load_model()

        # Get the path to the database file
        self.db_file = "learning.db"
        
        # check if database is already present
        if os.path.exists(self.db_file):
            self.train()
        else:
            self.create_database()

    def create_database(self) -> None:
        # Create the database
        conn = sqlite3.connect("learning.db")

        # Create the tables
        cur = conn.cursor()
        cur.execute("CREATE TABLE train_data (obstacles INTEGER, weather INTEGER, speed INTEGER, distance INTEGER, road_cond INTEGER, time INTEGER, risk_severity INTEGER)")
        cur.execute("CREATE TABLE test_data (obstacles INTEGER, weather INTEGER, speed INTEGER, distance INTEGER, road_cond INTEGER, time INTEGER, risk_severity INTEGER)")

        # generate 100 dataset to insert to the table
        for i in range(100):
            data = generate_data()

            # Insert data into the tables
            cur.execute("INSERT INTO train_data (obstacles, weather, speed, distance, road_cond, time, risk_severity) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
            cur.execute("INSERT INTO test_data (obstacles, weather, speed, distance, road_cond, time, risk_severity) VALUES (?, ?, ?, ?, ?, ?, ?)", data)

        # Commit the changes
        conn.commit()

        # Close the connection
        conn.close()

    def load_model(self) -> None:
        # Load the trained model state dictionary
        self.model.load_state_dict(torch.load("federated_model.pth"))
        self.model.eval()

    def train(self) -> None:
        # Load the train dataset
        train_dataset = CustomDataset(self.db_file, "train_data")
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

        model = self.model
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.0001)

        start_time = time.time()
        train_loss_l = []

        for epoch in range(num_epochs):
            # train the model
            model.train()
            train_loss = 0.0

            # Iterate over the data loader
            for batch_idx, (features, labels) in enumerate(train_loader):
                features, labels = features.to(device), labels.to(device)

                optimizer.zero_grad()
                output = model(features)
                loss = criterion(output, labels)
                loss.backward()
                optimizer.step()

                train_loss += loss.item() * features.size(0)
            train_loss /= len(train_loader.dataset)
            train_loss_l.append(train_loss)
        train = sum(train_loss_l) / num_epochs
        filepath = "results_training/train_loss.csv"
        write_to_csv(filepath, self.iterate, train)

        end_time = time.time()
        train_latency = end_time - start_time
        
        test_dataset = CustomDataset(self.db_file, "test_data")
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=True)
        model.eval()

        start_time = time.time()
        test_loss = 0.0
        for features, labels in test_loader:
            features, labels = features.to(device), labels.to(device)
            with torch.no_grad():
                output = model(features)
                loss = criterion(output, labels)
                test_loss += loss.item() * features.size(0)
            test_loss = test_loss / len(test_loader.dataset)
        end_time = time.time()
        test_latency = end_time - start_time

        filepath = "results_training/test_loss.csv"
        write_to_csv(filepath, self.iterate, test_loss)
        self.iterate += 1

        # Save the trained model
        torch.save(model.state_dict(), 'federated_model.pth')

        return train_latency, test_latency

    def predict(self, data) -> int:
        # Convert the input list to a tensor
        input_tensor = torch.tensor(data, dtype=torch.float32)

        # Reshape the input tensor to match the expected shape of the model
        input_tensor = input_tensor.view(1, -1)

        # Make the prediction
        with torch.no_grad():
            output = self.model(input_tensor)

        # Convert the predicted output to a single integer value
        predicted_label: int = torch.argmax(output).item()

        return predicted_label
    
if __name__ == "__main__":
    net = AI_Model()