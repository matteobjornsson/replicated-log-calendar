import socket
import threading

"""
Creates a message listening service on a separate thread.
This should be running on every node.
"""

lock = threading.Lock()
messageQueue = []

def thread_socket(c):
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
         lock.release()
         break
      
      msg = msg.decode("utf-8") #Decode messages for interpretation
      #TODO: Message has to be sent somewhere for usage.
      print(msg)
      #c.send("help".encode("utf-8"))
   c.close()

def listen():
   s = socket.socket()         # Create a socket object
   host = socket.gethostname() # Get local machine name
   port = 8080                # Reserve a port on EC2 instance
   s.bind(('', port))        # Bind to the port

   s.listen(5) #enable listening on socket

   while True:
      c, addr = s.accept()     # Establish connection from local
      print('Connection with', addr)
      lock.acquire() #lock for threading
      threading.Thread(target=thread_socket, args=(c,)).start()

   s.close()

if __name__ == "__main__":
   listen()
