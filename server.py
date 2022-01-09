import blockchain
import threading
import socket
import json

class Server:
    def __init__(self, myport, myblockchain):
        self.socket_host = "127.0.0.1"
        self.socket_port = myport
        self.myblockchain = myblockchain
        self.node_address = []
        mythread = threading.Thread(target=self.listening_to_connection)
        mythread.start()
    
    def listening_to_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mysocket:
            mysocket.bind((self.socket_host, self.socket_port))
            mysocket.listen()
            while True:
                conn, address = mysocket.accept()
                client_handler = threading.Thread(
                    target=self.receive_socket_message,
                    args=(conn, address)
                )
                client_handler.start()
    
    def receive_socket_message(self, connection, address):
        with connection:
            print(f"Connected by {address}")
            chunk_list = []
            # TODO: What if there are several requests arrived at the same time
            while True:
                chunk = connection.recv(4096)
                if not chunk:
                    break
                chunk_list.append(chunk)
            if len(chunk_list):
                message = b"".join(chunk_list)
                message_dict = json.load(message)
                response = ""
                if message_dict["request"] == "get_balance":
                    print("get_balance")
                elif message_dict["request"] == "transaction":
                    print("transaction")
                elif message_dict["request"] == "clone_blockchain":
                    print("clone_blockchain")
                elif message_dict["request"] == "broadcast_block":
                    print("broadcast_block")
                elif message_dict["request"] == "broadcast_transaction":
                    print(f"Receive transaction broadcast from {address}")
                    self.myblockchain.add_transaction(message_dict["data"])
                elif message_dict["request"] == "add_node":
                    print(f"Receive adding node requests from {address}")
                    connection_tuple = (message_dict["address"], int(message_dict["port"]))
                    if connection_tuple not in self.node_address:
                        self.node_address.append(connection_tuple)
                else:
                    print("Wrong request")
                if response != "":
                    connection.sendall(response)
