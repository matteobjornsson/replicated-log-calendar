import socket
import threading 
import argparse
from time import sleep

class Messenger:

    nodes = [(1, "localhost", 8081), (2, "localhost", 8082), 
             (3, "localhost", 8083), (4, "localhost", 8084)]

    out_sockets = []
    in_socket_threads = []
    connection_thread = None
    message_queue = []

    def __init__(self, nodeSelf: int):
        '''
        Constructor for the Messenger Class

        takes in an integer telling messenger what node number it is. 
        creates socket connections to all other nodes. 
        '''
        self.nodeID = nodeSelf

        self.connection_thread = (
            threading.Thread(
                target=self.init_incoming_message_threads).start()
        )
    def startup_outgoing_connections(self):
        for i in range(0,3):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            


    def init_incoming_message_threads(self):
        s = socket.socket()
        host = socket.gethostname()
        # TODO: add a try catch block in case s.bind() the port is busy
        s.bind(('', self.nodes[self.nodeID-1][2]))
        s.listen(4)

        while True:
            c, addr = s.accept() 
            self.in_socket_threads.append(
                threading.Thread(
                    target=self.message_collector_thread, 
                    args=(c, self.nodes[self.nodeID-1][2]),
                ).start()
            )
            print(self.in_socket_threads)
            print(threading.enumerate())
            
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