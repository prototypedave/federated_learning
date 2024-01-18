#!/usr/bin/env python3
"""
"""
import socket, threading, pickle
from logger import *
from typing import List
from funcs import *

class SdnController:
    def __init__(self, switch: List, vehicle: List, swich: int, port: int, dir: str) -> None:
        logger.info(f"SDN CONTROLLER STARTED")
        self.switches: List = switch
        self.vehicles: List = vehicle
        self.swich = swich
        self.port = port
        self.stop_flag = False
        self.dir = dir

    def listen(self):
        # set up listening port for the controller
        c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_sock.bind(('127.0.0.1', self.port))
        
        while not self.stop_flag:
            c_sock.listen(100)

            logger.info(f"SDN controller listening on port {self.port}")

            while True:
                # Accept incoming connection
                sock, address = c_sock.accept()
                logger.info(f"Sdn accepted connection from {address}")
        
                # Start a new thread to handle the client
                handler = threading.Thread(target=self.receive_critical_message, args=(sock,))
                self.receive_critical_message(sock)
        c_sock.close()

    def receive_critical_message(self, sock) -> None:
        # Receive data from the client
        data = sock.recv(1024)
        if not data:
            # If no data is received, the client has closed the connection
            logger.error(f'Sdn Lost connection to port')
            return
        # Process the received data
        pkt: List = pickle.loads(data)
        logger.info(f'Sdn received critical message from Switch')

        self.assign_configurations(pkt)

    def assign_configurations(self, data: List) -> None:
        openflow_msg: List = []
        # retrieve data
        if data is not None and len(data) == 6:
            src: int = data[0]
            dest: int = data[1]
            risk: int = data[2]
            speed: int = data[3]
            distance: int = data[4]
            tm = data[5]

            if distance == 0:
                distance = 1

            # calculate qos
            qos =  (risk + speed) / distance

            # assign destination switch
            switch_port, dist, port2 = self.get_destination_switch(dest)

            # get bandwidth
            bandwidth = calculate_bandwidth(qos)
            openflow_msg.append(bandwidth)

            # get bitrate
            bitrate = calculate_bitrate(speed=speed, distance=distance)
            openflow_msg.append(bitrate)

            # get number of antennas
            antenna = calculate_num_antennas(dist=dist)
            openflow_msg.append(antenna)

            # get processor speed
            processor = (qos * 2) / 160    # Assume a limited processor of 2Ghz and a max qos of 160
            openflow_msg.append(processor)

            # get memory
            ram = (qos * 1024) / 160
            openflow_msg.append(ram)

            openflow_msg.append(port2)
            openflow_msg.append(dest)

            # get action
            action = self.assign_action(qos)
            openflow_msg.append(action)

            openflow_msg.append(tm)
            openflow_msg.append(src)
            openflow_msg.append(speed)
            openflow_msg.append(distance)

            # get overhead
            overhead = network_overhead(bandwidth=bandwidth, bitrate=bitrate, antennas=antenna)
            filepath = self.dir + "network_overhead.csv"
            write_to_csv(filepath=filepath, x=speed, y=overhead)

            filepath = self.dir + "overhead_density.csv"
            write_to_csv(filepath=filepath, x=src, y=overhead)

            # get complexity
            complexity = computational_complexity(processor=processor, ram=ram)
            filepath = self.dir + "computational_complexity.csv"
            write_to_csv(filepath=filepath, x=speed, y=complexity)

            filepath = self.dir + "complexity_density.csv"
            write_to_csv(filepath=filepath, x=src, y=complexity)

            # routing decision
            rat = 100 - ((distance/1000) * 100)
            filepath = self.dir + "routing_vehicles.csv"
            write_csv(filepath=filepath, x=distance, y=src, z=rat)
            filepath = self.dir + "routing_speed.csv"
            write_csv(filepath=filepath, x=distance, y=speed, z=rat)

            # collision risk
            c_risk = calculate_collision_risk(distance=distance)
            filepath = self.dir + "collision_rate_speed.csv"
            write_csv(filepath=filepath, x=speed, y=c_risk, z=distance)
            filepath = self.dir + "collision_rate_veh.csv"
            write_csv(filepath=filepath, x=src, y=c_risk, z=distance)

            self.send_to_switch(openflow_msg, switch_port)



    def send_to_switch(self, msg: List, port: int) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('0.0.0.0', port))

        # convert data into bytes
        data = pickle.dumps(msg)
        sock.send(data)

        logger.info(f"Open flow message sent to switch at port {port}")
        
        sock.close

    
    def get_destination_switch(self, dst: int) -> tuple:
        # get the position of the destination vehicle
        pos1: int = 0
        port2: int = 0

        for vcl in self.vehicles:
            if vcl.id == dst:
                pos1 = vcl.distance
                port2 = vcl.port
        
        positions: List = []

        for swch in self.switches:
            pos = swch.distance
            positions.append(pos)

        idx, pos2 = get_node_address(positions, pos1)
        port = self.switches[idx].port

        dist = abs(pos2 - pos1)
        
        return port, dist, port2
        
    def assign_action(self, qos) -> str:
        action: str = ""
        if qos > 107:
            action = "Slow down"
        elif qos > 54:
            action = "maintain a steady speed"
        else:
            action = "watch out"
        return action