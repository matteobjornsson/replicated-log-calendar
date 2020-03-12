import socket
import threading 
import argparse
import pickle
from time import sleep

class Messenger:

    nodes = [(1, "localhost", 8081, [2,3,4]), (2, "localhost", 8082, [1,3,4]), 
             (3, "localhost", 8083, [1,2,4]), (4, "localhost", 8084, [1,2,3])]

    out_sockets = {}
    in_socket_threads = []
    allThreads = []
    message_queue = []
    

######## Constructor ###### 

    def __init__(self, nodeSelf: int):
        '''
        Constructor for the Messenger Class

        Initializes socket connections to all other nodes. 

        @Param:
            nodeSelf:: defines the ID of this node
        '''
        self.nodeID = nodeSelf
        self.otherNodes = self.nodes[self.nodeID-1][3] 

        # start a thread to grant incoming connections from other nodes
        connection_thread = (
            threading.Thread(
                target=self.init_incoming_message_threads))
        connection_thread.start()                   # start the thread
        self.allThreads.append(connection_thread)   # store for later reference

        # Start a thread for each node to acquire a connection to it 
        self.init_outgoing_connections()
        
        # join all initialization threads
        for t in self.allThreads:
            t.join()

        print("\n** NODE ", self.nodeID, " connected to all other nodes. **\n")

###### Initialization Methods ###### 

    def init_outgoing_connections(self):
        '''
        This method creates a socket for each node other than self, creating 
        a thread for that socket which tries to connect to the other node. 
        '''

        # generate 3 sockets and store them for reference
        for node in self.otherNodes:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.out_sockets[node] = s
            print(self.out_sockets)

        # for each socket assign it a node and thread to connect to that node
        for node in self.otherNodes:
            hostSocket = self.out_sockets[node]
            destinationNode = node
            destinationIP = self.nodes[destinationNode-1][1]
            destinationPort = self.nodes[destinationNode-1][2]
            
            # connection is threaded because the other nodes may or may not 
            # be running or accepting connections yet
            x = threading.Thread(
                target=self.connect_socket,
                args=(hostSocket,
                      destinationIP,
                      destinationPort,
                      destinationNode
                ))
            x.start()
            self.allThreads.append(x) #threads stored for reference


    def connect_socket(self, s: socket, host_ip: str, port: int, destination: int):
        '''
        Method takes a socket and connection parameters and connects to that 
        destination. 

        @Param:
            s:: socket to be used to establish connection
            host_ip::   destination IP
            port::      destination Port
            destination::   node ID of destination. 
        '''
        while True:
            try:# attempt to connect socket to other node
                s.connect((host_ip, port))
                print("Out socket connected to :", destination)
                break
            except socket.error:
                # while the connection fails, wait, and retry
                print("Connecting to ", destination, ".....")
                sleep(3)
                continue


    def init_incoming_message_threads(self):
        '''
        Method creates a socket that listens for incoming connections, assigning
        them to a new thread on arrival to accept messages from connection.
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # config
        host = socket.gethostname() # acquire self hostname
        s.bind(('', self.nodes[self.nodeID-1][2])) # bind to predetermined port
        s.listen(4) #accept up to 4 connections

        while True:
            c, addr = s.accept() # store the incoming connection in c, addr
            print("Input socket connected to: ", addr) 
            # start a thread with that connnection to listen for add'l msgs
            self.in_socket_threads.append(
                threading.Thread(
                    target=self.message_collector_thread, 
                    args=(c, ),
                ).start()
            )
            # once all three other nodes connect, end this thread. 
            if len(self.in_socket_threads)>2:
                break
            
    def message_collector_thread(self, connection):
        """
        Function to be threaded to collect messages and pass them to a msg queue.
        Eables message receiving.

        @Param:
            connection:: socket channel to listen on
        """
        #Continually listen for msgs
        while True:
            msg = connection.recv(1024)
            #report when a connection closes or fails. 
            if not msg:
                print("exiting socket")
                break
            msg = pickle.loads(msg)#Decode messages for interpretation
            self.message_queue.append(msg) # Append to msg queue
            print(msg)

    def test(self):
        while True:
            message = ("Message from Node {} : ".format(self.nodeID) + '\"' 
                        + input("\nType a message to send to the other nodes:\n") 
                        + '\"')
            for node in self.otherNodes:
                self.send(node, message)

######  Normal Operation Methods ###### 
    
    def send(self, N, m):
        message = pickle.dumps(m)
        self.out_sockets[N].sendall(message)

    
######  Recovery Methods ######
    # TODO:
    # methods here for detecting node loss and allowing to reconnect
    # might be able to use @init_incoming_message_threads() again



if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='Messenger Utility')
    parser.add_argument('nodeID', help='NodeID.', type=int)
    args = parser.parse_args()

    messenger = Messenger(args.nodeID)
    messenger.test()
