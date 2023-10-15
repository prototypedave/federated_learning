import socket
import threading
import pickle

# Function to handle incoming packets
def handle_client(client_socket):
    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        if not data:
            # If no data is received, the client has closed the connection
            break
        # Process the received data
        data = pickle.loads(data)
        print("Received data:", data)

# Function to create a socket listener
def start_server():
    # Define the server address and port
    server_address = ('0.0.0.0', 12345)
    
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the server address and port
    server_socket.bind(server_address)
    
    # Listen for incoming connections
    server_socket.listen(5)
    print("Server listening on port 12345")
    
    while True:
        # Accept incoming connection
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from {}:{}".format(client_address[0], client_address[1]))
        
        # Start a new thread to handle the client
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def send_to_controller(data, port) -> None:
    # start the socket for transmission
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', port))

    # convert data into bytes
    data = pickle.dumps(data)
    sock.send(data)
        
    sock.close

if __name__ == "__main__":
    # Start the server in the background
    for i in range(2):
        server_thread = threading.Thread(target=start_server)
        server_thread.start()
        port = 12345
        data = [1,2,3,4,5]
        send_to_controller(data, port)
