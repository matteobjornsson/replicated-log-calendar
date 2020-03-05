import socket

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 8080                # Reserve a port on EC2 instance
s.bind(('', port))        # Bind to the port
print(host)


s.listen(5)
c, addr = s.accept()     # Establish connection from local
print('Got connection from', addr)
while True:
   msg = c.recv(1024)
   if msg != None:
      if msg != '':
         msg = msg.decode("utf-8")
         print(msg)
         c.send(b'kfjndkfndsk')

c.close() 
