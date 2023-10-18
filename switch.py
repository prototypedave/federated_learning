#!/usr/bin/python3

"""
"""

from typing import List
import socket, pickle
from logger import *
import threading, time
from funcs import write_csv


class GnbSwitch:
    def __init__(self, idx: int, pos: int, port: int, controller_port: int, v_port: int, num_v: int, dir: str) -> None:
        # initialize this class
        self.index = idx
        self.dir = dir

        # set 5g variables
        self.bandwidth: int = 0
        self.bitrate: int = 0
        self.antennas: int = 0

        # set storage parameters
        self.processor: int = 0
        self.memory: int = 0

        # positional parameter
        self.distance: int = pos

        # transmission ports
        self.port: int = port
        self.c_port: int = controller_port
        self.v_port: int = v_port

        # self number of vehicles to connect to
        self.num_v: int = num_v

        self.stop_flag = False

        self.start = time.time()
        self.times: List = []

        self.count: int = 0

    def send_to_controller(self, data) -> None:
        # start the socket for transmission
        data_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', self.c_port))
        
        pkt: tuple = pickle.loads(data)
        print(pkt)
        spd = pkt[3]
        sock.send(data)       
        sock.close()

        self.count += 1

        end = time.time()
        vi = end - data_time
        rn_time = end - self.start

        v21 = vi / rn_time * 100

        filepath = self.dir + "v21_vehicles.csv"
        write_csv(filepath, rn_time, v21, self.count)

        filepath = self.dir + "v21_speed.csv"
        write_csv(filepath, rn_time, v21, spd)

    def listening_to_vehicles(self) -> None:
        # create a listening port for the switch to communicate with the vehicle
        server_address = ('127.0.0.2', self.v_port)
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(server_address)

        while not self.stop_flag:
            server_sock.listen(self.num_v)  # listen to a maximum of given connections
            logger.info(f"switch {self.index} listening for Vehicles on port {self.v_port}")

            while True:
                # Accept incoming connection
                sock, address = server_sock.accept()
                logger.info(f"Switch {self.index} accepted connection from {address}")

                data = sock.recv(1024)
                if not data:
                    # If no data is received, the client has closed the connection
                    logger.error(f'Switch {self.index} Lost connection to port {address}')
                    break

                # Start a new thread to handle the client
                handler = threading.Thread(target=self.send_to_controller, args=(data,))
                logger.info(f"Switch {self.index} just forwarded csm to controller")
                self.send_to_controller(data)
        server_sock.close()

    def configure(self, pkt: List) -> None:
        # catch ivalid packets
        if pkt is not None:
            # configure network resorces
            self.bandwidth = pkt[0]
            self.bitrate = pkt[1]
            self.antennas = pkt[2]

            # configure memory resources
            self.processor = pkt[3]
            self.memory = pkt[4]

            logger.info(
                f'Switch configured: Bandwidth {self.bandwidth}, Bitrate {self.bitrate}, Processor {self.processor}'
                )

            # get the remaining data
            action_port: int = pkt[5]
            dest = pkt[6]
            action = pkt[7]
            tm = pkt[8]
            src = pkt[9]
            spd = pkt[10]
            dst = pkt[11]
            msg: tuple = [dest, action, tm, src, spd, self.bandwidth, dst]

            # send critical message
            self.send_action(msg, action_port)

        else:
            raise LookupError(f"{logger.warning('Packet Not Full')}")
        
    def listening_server(self) -> None:
        # create a listening port for the switch to communicate with the controller
        server_address = ('0.0.0.0', self.port)
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(server_address)

        while not self.stop_flag:
            server_sock.listen(100)  # listen only on sdn
            logger.info(f"switch {self.index} listening for SDN controller on port {self.port}")

            while True:
                # Accept incoming connection
                sock, address = server_sock.accept()
                logger.info(f"Accepted SDN connection from {address}")
        
                # Start a new thread to handle the client
                handler = threading.Thread(target=self.handle_controller, args=(sock,))
                self.handle_controller(sock)
        server_sock.close()

    def handle_controller(self, sock) -> None:
        # listen to the controller in background
        # Receive data from the client
        data = sock.recv(1024)
        if not data:
            # If no data is received, the client has closed the connection
            logger.error(f'Lost connection with SDN')
            return
        # Process the received data
        pkt: List = pickle.loads(data)
        logger.info(f"{pkt}")
        logger.info(f'openflow configuration message received')

        # configure the switch
        self.configure(pkt)

    def send_action(self, msg: tuple, port: int) -> None:
        # send msg to vehicle
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', port))

        # convert data into bytes
        data = pickle.dumps(msg)
        sock.send(data)
        
        sock.close

    def reset(self) -> None:
        # reset the system back to its state
        pass