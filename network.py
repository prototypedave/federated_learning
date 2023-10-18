#!/usr/bin/env python3

"""
"""

from vehicle import Vehicle
from typing import List
from switch import GnbSwitch
import random,threading, time
from logger import logger
from controller import SdnController
from funcs import get_node_address, write_to_csv
from edge import EdgeServer


class Network:
    def __init__(self, vehicles: int, switch: int, dir: str) -> None:
        # store the vehicles instances in a list
        self.dir = dir
        self.vehicles: List[Vehicle] = []
        self.switches: List[GnbSwitch] = []
        self.v_port = 11000
        self.s_port = 14000
        self.c_port = 6653
        self.r_port = 16000

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
        self.controller = SdnController(self.switches, self.vehicles, switch, self.c_port, self.dir)

        # threading flag
        self.stop_flag: bool = False
        self.all_threads: List = []
        self.open_listening_ports()
        
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
            vehicle = Vehicle(index=idx, port=port, dir=self.dir)
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
            sw = GnbSwitch(idx=id, pos=ps, port=port, controller_port=self.c_port, v_port=pr, num_v=num, dir=self.dir)
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

    def open_listening_ports(self) -> None:
        # start the controller
        c_thread = threading.Thread(target=self.controller.listen)
        c_thread.start()
        self.all_threads.append(c_thread)

        # start the switches server
        for swch in self.switches:
            s_thread = threading.Thread(target=swch.listening_server)
            s_thread.start()
            self.all_threads.append(s_thread)
            
            # listening for vehicles
            sv_thread = threading.Thread(target=swch.listening_to_vehicles)
            sv_thread.start()
            self.all_threads.append(sv_thread)
        
        # start vehicles port
        for veh in self.vehicles:
            v_thread = threading.Thread(target=veh.receive_action)
            v_thread.start()
            self.all_threads.append(v_thread)

    def close_listening_ports(self) -> None:
        # still not fully implemented, find a way to close all threads with this func
        self.stop_flag = True
        for vehicle in self.vehicles:
            vehicle.stop_flag = self.stop_flag

        for swich in self.switches:
            swich.stop_flag = self.stop_flag

        self.controller.stop_flag = self.stop_flag

        for thread in self.all_threads:
            thread.join()

        logger.info(f"All connections closed")


    def load_dataset_for_baseline(self) -> None:
        # get the dataset of each vehicle and save it to db
        for vehicle in self.vehicles:
            vehicle.get_environment_data(self.obstacles, self.weather, self.road_data, self.time)
            vehicle.save_dataset()

    def run(self, model) -> None:
        # train the vehicle
        for vehicle in self.vehicles:
            vehicle.train_model(model)
            time.sleep(0.1)

            # make a prediction and create csm based on the training
            msg = vehicle.create_critical_message(self.vehicle_distance)

            # get the switch and its port to forward csm
            idx, pos = self.get_switch_index(vehicle.distance)
            port = self.switches[idx].v_port

            # send csm
            vehicle.send(port, msg)

    def get_packet_drops(self):
        count = 0
        filepath = self.dir + "packet_drop.csv"
        file = self.dir + "packet_drop_speed.csv"
        drop = 0
        for vehicle in self.vehicles:
            drop += vehicle.dropped_packets
            count += 1
            write_to_csv(filepath, count, drop)
            
            speed = vehicle.speed
            packet = vehicle.dropped_packets
            write_to_csv(file, speed, packet)

    def end(self):
        for swch in self.switches:
            swch.reset()
        logger.info(f"End of simulation")
            
        
if __name__ == '__main__':
    model = EdgeServer()
    net = Network(10, 1)
    net.load_dataset_for_baseline()
    net.run(model)
    net.close_listening_ports
        
