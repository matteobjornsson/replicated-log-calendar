import socket
import threading
from time import sleep 
import argparse

class Messenger:

    connection_list = []
    thread_list = []
    message_queue = []


    def __init__(self, nodeID: int, N: list):
        '''
        takes in list of tuples that represent other nodes in system to connect
        to: (nodeID: int, nodeIP: str)

        creates that many socket connections and stores them in a list
        '''

        # initialize socket connections, store them in list
        self.nodeID = nodeID
        self.Nodes = N
        self.s = socket.socket()         # Create a socket object
        self.host = socket.gethostname() # Get local machine name
        self.port = 8080     # Reserve a port on EC2 instance
        self.s.bind(('', self.port))     # Bind to the port
        self.s.listen(5) #enable listening on socket
        
        # if there are already nodes up and running, connect to them
        if N != []:
            for node in N:
                self.connectToExistingNode(node[1], node[0])

        # listen for new connections while initializing all 4 nodes
        while True:
            c, addr = self.s.accept()     # Establish connection from port
            print('Connection with', addr)
            self.addIncomingConnection(c) # pass off this connection to a new thread to listen for messages from that connection
            self.connection_list += [c]   # save specifically the connection for later
            #print(threading.enumerate())   
            #print(self.connection_list)
            return_msg = bytes("talkin back!", 'utf-8') 
            for conn in self.connection_list: #testing the connections received and stored
                conn.send(return_msg)


    # this method accepts a connection and starts a new thread to listen to it
    # adding incoming messages to a global queue
    def thread_socket(self, c):
        """
        Function to be threaded.
        Eables message receiving.

        @Param:
            c:: socket channel to listen on
        """
        while True:
            msg = c.recv(1024)
            if not msg:
                print("exiting socket")
                #lock.release()
                break
            msg = msg.decode("utf-8") #Decode messages for interpretation
            self.message_queue.append(msg)
            print(msg)

    # method takes a connection and starts a new thread to handle messages incoming on that connection
    def addIncomingConnection(self, connection):
        self.thread_list.append(threading.Thread(target=self.thread_socket, args=(connection,)).start())

    # given the details of an existing node, connect to that node
    # TODO: figure out how to store the connection for later use
    def connectToExistingNode(self, destinationIP:int, destinationNodeID: int):

        try: 
            # creating a TCP socket locally 
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            print("Socket successfully created")
        except socket.error as err: 
            print("socket creation failed with error %s" %(err))

        # this port is open on the EC2 instance
        port = 8080
  
        try: 
            # connect to this open port on this EC2 instance's IP 
            host_ip = socket.gethostbyname(destinationIP) 
            s.connect((host_ip, port)) 
            #print('Connection with', addr)
            #self.connection_list += [c]
            #stringToSend = "this is from node {}".format(str(self.nodeID))
            # turn it to bytes to be sent
            #b = bytes(stringToSend, 'utf-8')
            #c.send(b)
            #c.send(b + "--".encode())
        except socket.gaierror: 
            # this means could not resolve the host 
            print("there was an error resolving the host")
            sys.exit() 



    def send(self, destination: int, message):
        print("sending to {}".format(str(destination)))

    def receive(self, message):
        print("message received")

    def encode(self, message):
        #pickle me
        print("encoded")
    
    def decode(self, message):
        #unpickle me
        print("decoded")

if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='Messenger Utility')
    parser.add_argument('nodeID', help='NodeID.', type=int)
    args = parser.parse_args()
    #messenger = Messenger(args.nodeID, [(1, "localhost")])

    messenger = Messenger(args.nodeID, []) 