import threading
import socket
import pickle

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
                try:
                    parsed_message = pickle.load(message)
                except:
                    print(f"Unable to parse {message}")
                response = ""
                if parsed_message["request"] == "get_balance":
                    print(f"Get the balance for {address}")
                    address = parsed_message[address]
                    balance = self.myblockchain.get_balance(address)
                    response = {
                        "address": address,
                        "balance": balance
                    }
                elif parsed_message["request"] == "transaction":
                    print(f"Start to add transaction for {address}")
                    new_transaction = parsed_message["data"]
                    result, result_message = self.myblockchain.add_transaction(
                        new_transaction,
                        parsed_message["signature"]
                    )
                    response = {
                        "result": result,
                        "result_message": result_message
                    }
                    if result:
                        self.broadcast_message_to_nodes("broadcast_transaction", new_transaction)
                elif parsed_message["request"] == "clone_blockchain":
                    print("clone_blockchain")
                    # TODO
                elif parsed_message["request"] == "broadcast_block":
                    print("broadcast_block")
                    # TODO
                elif parsed_message["request"] == "broadcast_transaction":
                    print(f"Receive transaction broadcast from {address}")
                    self.myblockchain.add_transaction(parsed_message["data"])
                elif parsed_message["request"] == "add_node":
                    print(f"Receive adding node requests from {address}")
                    connection_tuple = (parsed_message["address"], int(parsed_message["port"]))
                    if connection_tuple not in self.node_address:
                        self.node_address.append(connection_tuple)
                else:
                    print(f"Wrong request from {address}")
                    response = {
                        "message": "Unknown request"
                    }
                if response != "":
                    response_bytes = str(response).encode('utf-8')
                    connection.sendall(response_bytes)

    def broadcast_message_to_nodes(self, request, data=None):
        message = {
            "request": request,
            "data": data
        }
        for node_address in self.node_address:
            if node_address != (self.socket_host, self.socket_port):
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(node_address)
                client.sendall(pickle.dumps(message))
                client.close()
    