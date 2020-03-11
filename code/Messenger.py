import socket
import threading 
import argparse
from time import sleep

class Messenger:

    nodes = [(1, "localhost", 8081, [2,3,4]), (2, "localhost", 8082, [1,3,4]), 
             (3, "localhost", 8083, [1,2,4]), (4, "localhost", 8084, [1,2,3])]

    out_sockets = []
    in_socket_threads = []
    allThreads = []
    message_queue = []

    def __init__(self, nodeSelf: int):
        '''
        Constructor for the Messenger Class

        takes in an integer telling messenger what node number it is. 
        Creates socket connections to all other nodes. 
        '''
        self.nodeID = nodeSelf

        connection_thread = (
            threading.Thread(
                target=self.init_incoming_message_threads)
            )
        connection_thread.start()
        self.allThreads.append(connection_thread)

        self.startup_outgoing_connections()
        for t in self.allThreads:
            t.join()

        print("NODE ", self.nodeID, " connected to all other nodes.")


    def startup_outgoing_connections(self):
        nodesConnected = 0
        otherNodes = self.nodes[self.nodeID-1][3]

        for i in range(0,3):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.out_sockets.append(s)

        for i in range(0,3):
            hostSocket = self.out_sockets[i]
            destinationNode = otherNodes[i]
            destinationIP = self.nodes[destinationNode-1][1]
            destinationPort = self.nodes[destinationNode-1][2]

            x = threading.Thread(
                target=self.connect_socket,
                args=(hostSocket,
                      destinationIP,
                      destinationPort,
                      destinationNode
                ))
            x.start()
            self.allThreads.append(x)


    def connect_socket(self, s: socket, host_ip: str, port: int, destination: int):
        while True:
            try:
                s.connect((host_ip, port))
                print("Out connected to :", destination)
                break
            except socket.error:
                print("Connecting to ", destination, ".....")
                sleep(3)
                continue


    def init_incoming_message_threads(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = socket.gethostname()
        # TODO: add a try catch block in case s.bind() the port is busy
        while True:
            try:
                s.bind(('', self.nodes[self.nodeID-1][2]))
                break
            except socket.error:
                sleep(5)
                continue
        s.listen(4)

        while True:
            c, addr = s.accept()
            print("In connected to: ", addr) 
            self.in_socket_threads.append(
                threading.Thread(
                    target=self.message_collector_thread, 
                    args=(c, self.nodes[self.nodeID-1][2]),
                ).start()
            )

            if len(self.in_socket_threads)>2:
                break
            
    def message_collector_thread(self, connection, selfPort:int):
        """
        Function to be threaded.
        Eables message receiving.

        @Param:
            c:: socket channel to listen on
        """
        while True:
            msg = connection.recv(1024)
            if not msg:
                print("exiting socket")
                #lock.release()
                break
            msg = msg.decode("utf-8") #Decode messages for interpretation
            self.message_queue.append(msg)
            print(msg)


if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='Messenger Utility')
    parser.add_argument('nodeID', help='NodeID.', type=int)
    args = parser.parse_args()

    messenger = Messenger(args.nodeID)