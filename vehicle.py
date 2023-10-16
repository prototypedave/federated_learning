#!/usr/bin/env python3

""" Class Vehicle """

from funcs import *
from typing import List
from edge import EdgeServer
import socket, pickle, time
import sqlite3
from logger import *
import threading

class Vehicle:
    # initializes the vehicle
    def __init__(self, index: int, port: int) -> None:
        self.id: int = index
        self.distance: int = random.randint(1, 900)  # 600 metres
        self.speed: int = random.randint(50, 150)   # 50km/hr - 150km/hr

        self.data: List[int] = [0, 0, 0, 0, 0, 0, 0]

        # uses the baseline model
        self.prediction: int = 0

        # transmission ports
        self.port = port

    def get_environment_data(self, obstacles: str, weather: str, r_condition: str, tim: str) -> None:
        # convert the values of the data into integer
        obs = obstacles_data(obstacles=obstacles)
        wth = weather_data(weather=weather)
        spd = speed_data(speed=self.speed)
        dist = distance_data(distance=self.distance)
        rdc = road_data(road=r_condition)
        tm = time_data(time=tim)
        rs = calculate_rs(obs, wth, spd, dist, rdc, tm)

        self.data = [obs, wth, spd, dist, rdc, tm, rs]
        
    
    def train_model(self) -> int:
        # trains the model using the baseline from Edge server and returns the learning summary
        model: EdgeServer = EdgeServer()
        data = self.data[:6]

        # trains the model with the generated dataset
        summary = model.train_each_vehicle(data)

        # makes prediction
        self.prediction: int = model.prediction(data)
 
        return summary, self.prediction
    
    def positive_alert(self, prediction: int) -> bool:
        # checks if the prediction is a positive risk
        if prediction >= 5:
            return True
        
        return False
            
    def create_critical_message(self, dist: List) -> tuple:  
        # get the source address
        src = self.id

        # get destination address
        dst, pos2 = get_node_address(dist=dist, pos=self.distance)

        # get the risk severity
        rs = self.prediction

        # get vwehicle speed
        vs = self.speed

        # get the risk distance
        rd = abs(pos2 - self.distance)

        message: tuple = (src, dst, rs, vs, rd)
    
        return message
    
    def send(self, port: int, msg: tuple) -> None:
        # start the socket for transmission
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('0.0.0.0', port))

        # convert data into bytes
        data = pickle.dumps(msg)
        sock.send(data)

        logger.info(f"Vehicle {self.id} just sent csm to Switch at port {port}")
        sock.close()

    def receive_action(self) -> None:
        # keeps the socket running
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', self.port))
        sock.listen(1)
        while True:
            try:
                conn, addr = sock.accept()
                data = conn.recv(1024)
                pkt = pickle.loads(data)
                name = self.id
                print(f"Vehicle {name}: Critical Message Received! Action taken")
                
                conn.close()
            
            except socket.error as e:
                # retry accepting connection after some time
                time.sleep(0.1)

    def listening(self) -> None:
        # create a listening port for the switch to communicate with the controller
        vehicle_address = ('127.0.0.1', self.port)
        vehicle_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        vehicle_sock.bind(vehicle_address)

        vehicle_sock.listen(5)  # listen to a maximum of 5 connections
        logger.info("Vehicle is open for communication")

        while True:
            # Accept incoming connection
            sock, address = vehicle_sock.accept()
            logger.info(f"Accepted connection from {address}: {sock}")
        
            # Start a new thread to handle the client
            handler = threading.Thread(target=self.handle_switch, args=(sock,))
            self.handle_controller.start()

    def handle_switch(self, sock) -> None:
        # listen to the controller in background
        while True:
            # Receive data from the client
            data = sock.recv(1024)
            if not data:
                # If no data is received, the client has closed the connection
                logger.error(f'Lost connection to port {sock}')
                break
            # Process the received data
            pkt: List = pickle.loads(data)
            logger.info(f'Action Received')
            
    def save_dataset(self) -> None:
        # saves each vehicle's dataset to the database
        conn = sqlite3.connect("learning.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO train_data (obstacles, weather, speed, distance, road_cond, time, risk_severity) VALUES (?, ?, ?, ?, ?, ?, ?)", self.data)
        cur.execute("INSERT INTO test_data (obstacles, weather, speed, distance, road_cond, time, risk_severity) VALUES (?, ?, ?, ?, ?, ?, ?)", self.data)

        # Commit the changes
        conn.commit()

        # Close the connection
        conn.close()


if __name__ == "__main__":
    logger.debug('Start of testing')
    vehicle = Vehicle(0, 1000)
    print(f"\033[30m Vehicle position: {vehicle.distance}")
    print(f"\033[30m Vehicle speed: {vehicle.speed}")

    vehicle.get_environment_data('poor', 'rainy', 'potholes', 'day')
    print(f"\033[30m Vehicle generated data: {vehicle.data}")
    summary, pred = vehicle.train_model()
    print(f"\033[30m Model prediction: {pred}")

    dist = [20, 180, 290, 300, 412, 512, 653, 780, 899]
    msg = vehicle.create_critical_message(dist)
    print(f"\033[30m Generated message: {msg}")

    vehicle.save_dataset()
    logger.info('Test executed successfully')
    logger.debug('End of Test!')

