#!/usr/bin/env python3

"""
"""

from vehicle import Vehicle
from typing import List
from switch import GnbSwitch
import random,threading
from logger import logger
from controller import SdnController
from funcs import get_node_address


class Network:
    def __init__(self, vehicles: int, switch: int) -> None:
        # store the vehicles instances in a list
        self.vehicles: List[Vehicle] = []
        self.switches: List[GnbSwitch] = []
        self.v_port = 1234
        self.s_port = 2345
        self.c_port = 3456
        self.r_port = 4321

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
        self.get_switches(swch=switch, vehicles=vehicles)

        # store the distance for the switch
        self.switch_distance: List[int] = []
        self.get_switch_distance()

        # add controller
        self.cotroller = SdnController(self.switches, self.vehicles, switch, self.c_port)

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

    def get_switches(self, swch, vehicles) -> None:
        dif: int = int(900 / swch)
        pos: int = int(dif / 2)
        for id in range(swch):
            ps = 0
            if id == 0:
                ps = pos
            else:
                ps = pos + dif * id 
            port = self.s_port + id
            pr = self.r_port + id
            num = int(vehicles / swch)
            sw = GnbSwitch(idx=id, pos=ps, port=port, controller_port=self.c_port, v_port=pr, num_v=num)
            self.switches.append(sw)

        logger.info(f'Switches : {swch}')

    def get_switch_index(self, distance) -> int:
        idx, pos = get_node_address(self.switch_distance, distance)
        return idx, pos

    def get_distance(self) -> None:
        for vehicle in self.vehicles:
            dist = vehicle.distance
            self.vehicle_distance.append(dist)

    def get_switch_distance(self) -> None:
        for switch in self.switches:
            dist = switch.distance
            self.switch_distance.append(dist)
        
if __name__ == '__main__':
    net = Network(100, 10)
    # load the datasets
    for vehicle in net.vehicles:
        vehicle.get_environment_data(net.obstacles, net.weather, net.road_data, net.time)
        # save the dataset in db
        # vehicle.save_dataset()
    c_thread = threading.Thread(target=net.cotroller.listen)
    c_thread.start()

    for swich in net.switches:
        r_thread = threading.Thread(target=swich.listening_server)
        r_thread.start()

    # train the vehicle
    for vehicle in net.vehicles:
        vehicle.train_model()

        # create csm
        msg = vehicle.create_critical_message(net.vehicle_distance)

        idx, pos = net.get_switch_index(vehicle.distance)
        print(idx, pos)
    
        port = net.switches[idx].port

        switch_thread = threading.Thread(target=net.switches[idx].listening_to_vehicles)
        switch_thread.start()

        vehicle.send(port, msg)

        
