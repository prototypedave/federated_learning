#!/usr/bin/env python3

""" Class Vehicle """

from funcs import *
from typing import List
from edge import EdgeServer
import socket, pickle, time
import sqlite3
import logging
from colorlog import ColoredFormatter


# Set up the logging handler with a ColoredFormatter
handler = logging.StreamHandler()
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
handler.setFormatter(formatter)

# Set up the logger with the handler
logger = logging.getLogger('custom_logger')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class Vehicle:
    # initializes the vehicle
    def __init__(self, index: int, port: int) -> None:
        self.id: int = index
        self.distance: int = random.randint(0, 900)  # 600 metres
        self.speed: int = random.randint(50, 150)   # 50km/hr - 150km/hr

        self.data: List[int] = [0, 0, 0, 0, 0, 0, 0]

        # uses the baseline model
        self.model: EdgeServer = EdgeServer()
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
        data = self.data[:6]

        # trains the model with the generated dataset
        summary = self.model.train_each_vehicle(data)

        # makes prediction
        self.prediction: int = self.model.prediction(data)
 
        return summary, self.prediction
    
    def positive_alert(self, prediction: int) -> bool:
        # checks if the prediction is a positive risk
        if prediction >= 5:
            return True
        
        return False
            
    def create_critical_message(self, dist: List[int]) -> tuple:  
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
    
    def send(self, port: int) -> None:
        # start the socket for transmission
        sock = socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', port))

        # convert data into bytes
        data = pickle.dumps(self.data)
        sock.send(data)

        logger.info("Vehicle {self.id} just sent csm to Switch at port {port}")
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

