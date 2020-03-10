import socket
import threading

class Messenger:

    connection_list = []
    message_queue = []


    def __init__(self, N: list):
        '''
        takes in list of tuples that represent other nodes in system to connect
        to: (nodeID: int, nodeIP: str)

        creates that many socket connections and stores them in a list
        '''


        # initialize socket connections, store them in list

        self.Nodes = N
        self.s = socket.socket()         # Create a socket object
        self.host = socket.gethostname() # Get local machine name
        self.port = 8080                 # Reserve a port on EC2 instance
        self.s.bind(('', self.port))          # Bind to the port
        self.s.listen(5) #enable listening on socket
        
        while True:
            c, addr = self.s.accept()     # Establish connection from local
            print('Connection with', addr)
            self.addConnection(c)
            print(threading.enumerate())


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

    def addConnection(self, connection):
        self.connection_list.append(threading.Thread(target=self.thread_socket, args=(connection,)).start())

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
    messenger = Messenger([])

    