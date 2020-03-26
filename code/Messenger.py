import socket, threading, argparse, pickle, csv, ast
from time import sleep

class Messenger:

	out_sockets = {}
	in_sockets = {}
	in_socket_threads = []
	allThreads = []
	message_queue = []
	listen_socket = None

	localNodes =[(1, "localhost", 8081, [2,3,4]), (2, "localhost", 8082, [1,3,4]), 
			 (3, "localhost", 8083, [1,2,4]), (4, "localhost", 8084, [1,2,3])]
	

######## Constructor ###### 
	file_path = '../files/nodeAddresses.tsv'

	def __init__(self, nodeSelf: int, local: int):
		'''
		Constructor for the Messenger Class

		Initializes socket connections to all other nodes. 

		@Param:
			nodeSelf:: defines the ID of this node
		'''

		self.nodeID = nodeSelf
		if (local == 1):
			self.nodes = self.localNodes
		else: 
			self.nodes = self.read_in_node_addresses()
		self.otherNodes = self.nodes[self.nodeID-1][3] 
		
		self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
		self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # config
		port = self.nodes[self.nodeID-1][2]
		self.listen_socket.bind(('', port)) # bind to predetermined port
		self.listen_socket.listen(4) #accept up to 4 connections

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

	def read_in_node_addresses(self):
		nodes = []
		with open(self.file_path, 'r') as read_file:
			csv_reader = csv.reader(read_file, delimiter='\t')
			next(csv_reader)
			for line in csv_reader:
				otherNodes = [n for n in ast.literal_eval(line[3])]
				#if int(line[0]) == self.nodeID:
				#	n = (int(line[0]), 'localhost', int(line[2]), otherNodes)
				#else:
				n = (int(line[0]), line[1], int(line[2]), otherNodes)
				nodes.append(n)
				#print(n)
		return nodes

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
		counter = 0
		while True:
			try:# attempt to connect socket to other node
				s.connect((host_ip, port))
				#print("out socket from self ", self.nodeID, " to ", destination, " at ", self.out_sockets[destination])
				print("Out socket connected to :", destination)
				break
			except socket.error:
				# while the connection fails, wait, and retry
				if counter == 12:
					print("Connecting to node ", destination, " at ", host_ip, port, ' ......')
					counter = 0
				# debug print statemet to see how in socket thread count changes
				#for sthread in self.in_socket_threads:
				#	print(type(sthread))
				counter += 1
				sleep(.25)
				continue


	def init_incoming_message_threads(self):
		'''
		Method creates a socket that listens for incoming connections, assigning
		them to a new thread on arrival to accept messages from connection.
		'''
		while True:
			print('listening for incoming connections on ', self.listen_socket.getsockname() )
			c, addr = self.listen_socket.accept() # store the incoming connection in c, addr
			print("Input socket connected to: ", addr) 
			self.in_sockets[addr[1]] = c
			# start a thread with that connnection to listen for add'l msgs
			self.in_socket_threads.append(
				threading.Thread(
					target=self.message_collector_thread, 
					args=(c, ),
					daemon=True
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
		buffer_size = 1024
		while True:
			packet = b''
			while True:
				chunk = connection.recv(buffer_size)
				packet += chunk
				if len(chunk) < buffer_size:
					break
				
			#report when a connection closes or fails. 
			if not packet:
				failed_IP = connection.getpeername()[0]
				print("Failed IP: ", failed_IP)
				failed_node = 0
				for item in self.nodes:
					if item[1] == failed_IP:
						failed_node = item[0]
						break
				print("exiting socket. node ", failed_node, " failed")

				# reinstate connection: 
				self.reinit_failed_outgoing_connection(failed_node)
				self.reinit_incoming_message_thread()
				print("\n** NODE ", self.nodeID, " reconnected to ", failed_node, ". **\n")
				self.message_queue.append((2,))
				break
			# print("still in this thread")
			unpickled_message = pickle.loads(packet)#Decode messages for interpretation
			self.message_queue.append(unpickled_message) # Append to msg queue

######  Normal Operation Methods ###### 
	
	def send(self, N, m):
		message = pickle.dumps(m)
		self.out_sockets[N].sendall(message)

	
######  Recovery Methods ######
	# TODO:
	# methods here for detecting node loss and allowing to reconnect
	# might be able to use @init_incoming_message_threads() again

	def reinit_failed_outgoing_connection(self, failedNode: int):
		'''
		This method tries to reconnect the outgoing socket to the failed node. 
		'''

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.out_sockets[failedNode] = s

		hostSocket = self.out_sockets[failedNode]
		destinationNode = failedNode
		destinationIP = self.nodes[destinationNode-1][1]
		destinationPort = self.nodes[destinationNode-1][2]
		
		counter = 0
		while True:
			try:# attempt to connect socket to other node
				hostSocket.connect((destinationIP, destinationPort))
				#print("out socket from self ", self.nodeID, " to ", destination, " at ", self.out_sockets[destination])
				print("Out socket is reconnected to :", destinationNode)
				break
			except socket.error:
				# while the connection fails, wait, and retry
				if counter == 12:
					print("Connection has failed, reconnecting to node ", destinationNode, " at ", destinationIP, destinationPort, ' ......')
				# debug print statemet to see how in socket thread count changes
				counter += 1
				sleep(.25)
				continue
		

	def reinit_incoming_message_thread(self):
		print('listening for incoming connections on ', self.listen_socket.getsockname() )
		c, addr = self.listen_socket.accept() # store the incoming connection in c, addr
		print("Input socket reconnected to: ", addr) 
		self.in_sockets[addr[1]] = c
		# start a thread with that connnection to listen for add'l msgs
		self.in_socket_threads.append(
			threading.Thread(
				target=self.message_collector_thread, 
				args=(c, ),
				daemon=True
			).start()
		)

if __name__ == '__main__':
	parser =  argparse.ArgumentParser(description='Messenger Utility')
	parser.add_argument('nodeID', help='NodeID.', type=int)
	parser.add_argument('local', help='local or not', type=int)
	args = parser.parse_args()

	messenger = Messenger(args.nodeID, args.local)
	#messenger.test()
