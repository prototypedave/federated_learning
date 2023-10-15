#!/usr/bin/env python3

"""
"""

from vehicle import Vehicle
from typing import List
from switch import GnbSwitch
import random
from logger import logger
from controller import SdnController


class Network:
    def __init__(self, vehicles: int, switch: int) -> None:
        # store the vehicles instances in a list
        self.vehicles: List[Vehicle] = []
        self.switches: List[GnbSwitch] = []
        self.v_port = 12345
        self.s_port = 54321
        self.c_port = 6643

        # environment conditions
        self.obstacles: str = ""
        self.road_data: str = ""
        self.time: str = ""
        self.weather: str = ""
        self.environment_conditions()

        # add the vehicles to the list
        self.get_vehicles(vehicles)

        # store the distance in a list
        self.vehicle_distance: List[int] = []
        self.get_distance()

        # add switches
        self.get_switches(swch=switch)

        # add controller
        self.cotroller = SdnController(self.switches, self.vehicles)

    def environment_conditions(self) -> None:
        # obstacles
        cond1: List[str] = ["poor", "fair", "good"]
        self.obstacles = random.choice(cond1)

        # weather
        cond2: List[str] = ["rainy", "clear"]
        self.weather = random.choice(cond2)

        # road condition
        cond3: List[str] = ["potholes", "slippery", "clear"]
        self.road_data = random.choice(cond3)

        # time
        cond4: List[str] = ["day", "night"]
        self.time = random.choice(cond4)

        logger.info(f"===== Current Environment Conditions =====")
        logger.info(f"Obstacles :      {self.obstacles}")
        logger.info(f"Weather :        {self.weather}")
        logger.info(f"Road Condition : {self.road_data}")
        logger.info(f"Period :         {self.time}")

    def get_vehicles(self, veh) -> None:
        for idx in range(veh):
            port = self.v_port + idx
            vehicle = Vehicle(index=idx, port=port)
            self.vehicles.append(vehicle)
        logger.info(f'Vehicles : {veh}')

    def get_switches(self, swch) -> None:
        for id in range(swch):
            port = self.s_port + id
            pos = (900 % swch)    # 900 for max distace, we set the position o the switch on exact intervals
            if id > 0:
                pos = pos * id
            switch = GnbSwitch(idx=id, pos=pos, port=port, controller_port=self.c_port)
            self.switches.append(switch)
        logger.info(f'Switches : {swch}')

    def get_distance(self) -> None:
        for vehicle in self.vehicles:
            dist = vehicle.distance
            self.vehicle_distance.append(dist)
        
if __name__ == '__main__':
    net = Network(100, 10)
    for swch in net.switches:
        swch.configure(["p"])   

        