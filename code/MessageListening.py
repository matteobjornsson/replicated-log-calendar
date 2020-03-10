import socket
import threading

lock = threading.Lock()
messageQueue = []

def thread_socket(c):
   while True:
      global messageQueue
      msg = c.recv(1024).decode("utf-8")
      messageQueue.append(msg)
      print(msg)
      c.send("help".encode("utf-8"))


s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 8080               # Reserve a port on EC2 instance
s.bind(('', port))        # Bind to the port
print(host)

s.listen(5)

while True:
   #msg = c.recv(1024)
   c, addr = s.accept()     # Establish connection from local
   print('Connection with', addr)
   #lock.acquire()
   threading.Thread(target=thread_socket, args=(c,)).start()
   

   """
   if msg != None:
      if msg != '':
         msg = msg.decode("utf-8")
         print(msg)
         c.send(b'kfjndkfndsk')
   c.close()
   """ 
s.close()
