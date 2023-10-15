#!/usr/bin/python3

"""
"""

from typing import List
import socket, pickle
from logger import *
import threading


class GnbSwitch:
    def __init__(self, idx: int, pos: int, port: int, controller_port: int) -> None:
        # initialize this class
        self.index = idx

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

    def send_to_controller(self, data: List) -> None:
        # start the socket for transmission
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', self.c_port))

        # convert data into bytes
        data = pickle.dumps(data)
        sock.send(data)
        
        sock.close

    def configure(self, pkt: List) -> None:
        # catch ivalid packets
        if pkt is not None and len(pkt) == 8:
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
            msg: tuple = [dest, action]

            # send critical message
            self.send_action(msg, action_port)

        else:
            raise LookupError(f"{logger.warning('Packet Not Full')}")
        
    def listening_server(self) -> None:
        # create a listening port for the switch to communicate with the controller
        server_address = ('0.0.0.0', self.port)
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(server_address)

        server_sock.listen(5)  # listen to a maximum of 5 connections
        logger.info("switch {self.index} listening on port {self.port}")

        while True:
            # Accept incoming connection
            sock, address = server_sock.accept()
            logger.info(f"Accepted connection from {address}: {sock}")
        
            # Start a new thread to handle the client
            handler = threading.Thread(target=self.handle_controller, args=(sock,))
            self.handle_controller.start()

    def handle_controller(self, sock) -> None:
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
        self.bandwidth: int = 0
        self.bitrate: int = 0
        self.antennas: int = 0
        self.processor: int = 0
        self.memory: int = 0