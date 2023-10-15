#!/usr/bin/env python3
"""
"""
import socket, threading, pickle
from logger import *
from typing import List
from funcs import *

class SdnController:
    def __init__(self, switch: List, vehicle: List) -> None:
        self.switches: List = switch
        self.vehicles: List = vehicle

        # set up listening port for the controller
        self.port = 6643
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('127.0.0.1', self.port))
        self.sock.listen(5)

        logger.info("SDN controller listening on port {self.port}")

        while True:
            # Accept incoming connection
            sock, address = self.sock.accept()
            logger.info(f"Accepted connection from {address}: {sock}")
        
            # Start a new thread to handle the client
            handler = threading.Thread(target=self.receive_critical_message(), args=(sock,))
            self.handle_controller.start()

    def receive_critical_message(self, sock) -> None:
        while True:
            # Receive data from the client
            data = sock.recv(1024)
            if not data:
                # If no data is received, the client has closed the connection
                logger.error(f'Lost connection to port {sock}')
                break
            # Process the received data
            pkt: List = pickle.loads(data)
            logger.info(f'critical message received')

            self.assign_configurations(pkt)

    def assign_configurations(self, data: List) -> None:
        # retrieve data
        if data is not None and len(data) == 5:
            src: int = data[0]
            dest: int = data[1]
            risk: int = data[2]
            speed: int = data[3]
            distance: int = data[4]

            # calculate qos
            qos = sum(risk, speed) / distance

            # assign destination switch
            switch_port, dist, port2 = self.get_destination_switch(dest)

            # get bandwidth
            bandwidth = calculate_bandwidth(qos)

            # get bitrate
            bitrate = calculate_bitrate(speed=speed, distance=distance)

            # get number of antennas
            antenna = calculate_num_antennas(dist=dist)

            # get processor speed
            processor = (qos * 2) / 160    # Assume a limited processor of 2Ghz and a max qos of 160

            # get memory
            ram = (qos * 1024) / 160

            # get action
            action = self.assign_action(qos)

            openflow_msg: List = [bandwidth, bitrate, antenna, processor, ram, port2, dest, action]
            self.send_to_switch(openflow_msg, switch_port)

    def send_to_switch(msg: List, port: int) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('0.0.0.0', port))

        # convert data into bytes
        data = pickle.dumps(msg)
        sock.send(data)
        
        sock.close

    
    def get_destination_switch(self, dst: int) -> tuple:
        # get the position of the destination vehicle
        pos1: int = 0
        port2: int = 0

        for vcl in self.vehicles:
            if vcl.id == dst:
                pos1 = vcl.distance
                port2 = vcl.port
        
        positions: List = 0

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