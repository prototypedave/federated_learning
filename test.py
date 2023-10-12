import socket
import pickle
from typing import List
import time, threading

def send(port: int, data: List[int]) -> None:
    # start the socket for transmission
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', port))

    # convert data into bytes
    data = pickle.dumps(data)
    sock.send(data)

    print("Data sent")
    sock.recv(1024)

def receive_action(port) -> None:
    # keeps the socket running
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', port))
    sock.listen()
    conn, addr = sock.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            pkt = pickle.loads(data)
            print("data sent again")
            conn.sendall(data)

if __name__ == "__main__":
    # Example usage:
    port = 1024
    data = [1, 2, 3, 4, 5]
    t = threading.Thread(target=receive_action(port))
    t.start()
    send(port, data)
