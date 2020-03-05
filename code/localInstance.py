import socket # for socket 
import sys  


class createConnections:
    def __init__(self, node1IP, node2IP, node3IP):
        self.node1IP = node1IP
        self.node2IP = node2IP
        self.node3IP = node3IP

    def createConnections(self):
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
            host_ip = socket.gethostbyname(self.node1IP) 
            s.connect((host_ip, port)) 
        except socket.gaierror: 
            # this means could not resolve the host 
            print("there was an error resolving the host")
            sys.exit() 
        stringToSend = "this is where you put the stuff to be sent"
        # turn it to bytes to be sent
        b = bytes(stringToSend, 'utf-8')
        s.send(b)
        while True:
        # connecting to the server 
            msg = s.recv(1024)
            if msg != None:
                if msg != '':
                    msg = msg.decode("utf-8")
                    print(msg)

  
        print("the socket has successfully connected to google \ on port == %s" %(host_ip))


c = createConnections("18.233.10.196", None, None)
c.createConnections()