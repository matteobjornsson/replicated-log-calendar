import queue
import threading
from tabulate import tabulate
import copy
from numpy import inf
from typing import *


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.in_queue = queue.Queue(maxsize)
        self.out_queue = queue.Queue(maxsize)
    
    ##get packet from the queue interface
    # @param in_or_out - use 'in' or 'out' interface
    def get(self, in_or_out):
        try:
            if in_or_out == 'in':
                pkt_S = self.in_queue.get(False)
                # if pkt_S is not None:
                #     print('getting packet from the IN queue')
                return pkt_S
            else:
                pkt_S = self.out_queue.get(False)
                # if pkt_S is not None:
                #     print('getting packet from the OUT queue')
                return pkt_S
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param in_or_out - use 'in' or 'out' interface
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, in_or_out, block=False):
        if in_or_out == 'out':
            # print('putting packet in the OUT queue')
            self.out_queue.put(pkt, block)
        else:
            # print('putting packet in the IN queue')
            self.in_queue.put(pkt, block)
            
        
## Implements a network layer packet.
class NetworkPacket:
    ## packet encoding lengths 
    dst_S_length = 5
    prot_S_length = 1  #protocol indicates what type of packet (data vs control)
    
    ##@param dst: address of the destination host
    # @param data_S: packet payload
    # @param prot_S: upper layer protocol for the packet (data, or control)
    def __init__(self, dst, prot_S, data_S):
        self.dst = dst
        self.data_S = data_S
        self.prot_S = prot_S
        
    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst).zfill(self.dst_S_length)
        if self.prot_S == 'data':
            byte_S += '1'
        elif self.prot_S == 'control':
            byte_S += '2'
        else:
            raise('%s: unknown prot_S option: %s' %(self, self.prot_S))
        byte_S += self.data_S
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(cls, byte_S):
        dst = byte_S[0 : NetworkPacket.dst_S_length].strip('0')
        prot_S = byte_S[NetworkPacket.dst_S_length : NetworkPacket.dst_S_length + NetworkPacket.prot_S_length]
        if prot_S == '1':
            prot_S = 'data'
        elif prot_S == '2':
            prot_S = 'control'
        else:
            raise('%s: unknown prot_S field: %s' %(cls, prot_S))
        data_S = byte_S[NetworkPacket.dst_S_length + NetworkPacket.prot_S_length : ]        
        return cls(dst, prot_S, data_S)
    

    

## Implements a network host for receiving and transmitting data
class Host:
    
    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.intf_L = [Interface()]
        self.stop = False #for thread termination
    
    ## called when printing the object
    def __str__(self):
        return self.addr
       
    ## create a packet and enqueue for transmission
    # @param dst: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst, data_S):
        p = NetworkPacket(dst, 'data', data_S)
        print('%s: sending packet "%s"' % (self, p))
        self.intf_L[0].put(p.to_byte_S(), 'out') #send packets always enqueued successfully
        
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.intf_L[0].get('in')
        if pkt_S is not None:
            print('\n%s: received packet "%s"' % (self, pkt_S))
       
    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return
        


## Implements a multi-interface router
class Router:
    
    ##@param name: friendly router name for debugging
    # @param cost_D: cost table to neighbors {neighbor: {interface: cost}}
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name: str, cost_D: Dict, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.intf_L = [Interface(max_queue_size) for _ in range(len(cost_D))]
        #save neighbors and interfeces on which we connect to them
        self.cost_D = cost_D    # {neighbor: {interface: cost}}
        self.neighbors = []     # simple list of neighbors for each router
        for neighbor in cost_D:
            self.neighbors.append(neighbor)

        self.rt_tbl_D = {}  # {destination: {router: cost}}
        self.N = []         # list of nodes in network
        self.R = []         # list of routers in network
 

    # used to inform routers of the nodes in the network. 
    def update_network_nodes(self, N, R):
        self.N = N
        self.R = R
        

    # used to initialize routing table. Tables are initialized only knowing cost to neighbors. 
    def initialize_routing_table(self): 
        r_table = {}

        # initialize table with all distances = to infinity
        for node in self.N:
            r_table.update({node: {}})
            for router in self.R:
                r_table[node].update({router: inf})

        # fill in each cost for known neighbor
        for dest_key, intf_dict in self.cost_D.items():
            cost = intf_dict[next(iter(intf_dict))]
            r_table[dest_key].update({self.name : cost})

        #cost to self is 0
        r_table[self.name].update({self.name: 0})

        print('%s: Initialized routing table' % self)
        self.rt_tbl_D = r_table
        self.print_routes()

        
    ## Print routing table
    def print_routes(self):

        if not self.rt_tbl_D:
            print("\n Routing table is empty \n")
        else:
            headers = self.N    # Table headers will be all nodes on the network
            rowIDs = self.R     # Row headers will be all routers on the network.
            r_table = copy.deepcopy(self.rt_tbl_D) # Table copied to be formatted

            
            # This for loop flattens    {destination: {router: cost}} 
            #                     to    {destination: [cost1, cost2, ...}]} by router
            temp = []
            for m in headers:
                for n in rowIDs:
                    temp.append(r_table[m][n])
                r_table[m] = temp
                temp = []

            # Add the router name to the header list
            headers = ['*' + self.name + '*'] + headers

            # pretty print via tabular
            print(tabulate(r_table, headers, showindex=rowIDs, tablefmt="fancy_grid")+ '\n')



    ## called when printing the object
    def __str__(self):
        return self.name


    ## look through the content of incoming interfaces and 
    # process data and control packets
    def process_queues(self):
        for i in range(len(self.intf_L)):
            pkt_S = None
            #get packet from interface i
            pkt_S = self.intf_L[i].get('in')
            #if packet exists make a forwarding decision
            if pkt_S is not None:
                p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                if p.prot_S == 'data':
                    self.forward_packet(p,i)
                elif p.prot_S == 'control':
                    self.update_routes(p, i)
                else:
                    raise Exception('%s: Unknown packet type in packet %s' % (self, p))
            

    ## forward the packet according to the routing table
    #  @param p Packet to forward
    #  @param i Incoming interface number for packet p
    def forward_packet(self, p, i):
        try:
            # TODO: Here you will need to implement a lookup into the 
            # forwarding table to find the appropriate outgoing interface
            # for now we assume the outgoing interface is 1

            #self.rt_tbl_D
            #print("Destination: " + p.dst)

            fwd_intf = None

            # If destination is neighbor, just go there
            if p.dst in self.neighbors:
                fwd_intf = list(self.cost_D[p.dst].keys())[0]
            else:
                min_dist = inf
                fwd_router = None

                # Find the router with the minium distance to target, and choose that interface
                for routing_option in self.rt_tbl_D[p.dst].items():
                    if routing_option[0] in self.neighbors:
                        if routing_option[1] < min_dist:
                            min_dist = routing_option[1]
                            fwd_router = routing_option[0]

                fwd_intf = list(self.cost_D[fwd_router].keys())[0]
            
            #print("Forwarding Through Interface: " + str(fwd_intf))

            self.intf_L[fwd_intf].put(p.to_byte_S(), 'out', True)
            print('%s: forwarding packet "%s" from interface %d to %d' % \
                (self, p, i, fwd_intf))
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass

    ## send out route update
    # @param i Interface number on which to send out a routing update
    def send_routes(self, i):

        # send this node's distance vector to other routers
        distance_vector = {}
        # collect the distance to each node from self (according to current table)
        for node in self.N:
            cost_to_node = self.rt_tbl_D[node][self.name]
            distance_vector.update({node: {self.name: cost_to_node}})

        # flatten vector dict into string
        distance_vector_S = str(distance_vector)
        p = NetworkPacket(0, 'control', distance_vector_S)
        # send backet
        try:
            print('%s: sending routing update "%s" from interface %d' % (self, p, i))
            self.intf_L[i].put(p.to_byte_S(), 'out', True)
        except queue.Full:
            print('%s: packet "%s" lost on interface %d' % (self, p, i))
            pass


    ## forward the packet according to the routing table
    #  @param p Packet containing routing information
    def update_routes(self, p, i):
        print('%s received d vector' % (self.name) + p.data_S )
        neighbor_vector = eval(p.data_S)
        neighbor = next(iter(neighbor_vector[self.N[0]]))

        # add neighbor's distance vector to this routing table
        for node in self.N:
            self.rt_tbl_D[node].update({neighbor: neighbor_vector[node][neighbor]})
        self.print_routes

        # save current distance vector
        current_distance_vector = {}
        for node in self.N:
            cost_to_node = self.rt_tbl_D[node][self.name]
            current_distance_vector.update({node: {self.name: cost_to_node}})
        # shortening some variables for ease of use
        name = self.name
        table = self.rt_tbl_D
        neighbors2 = self.neighbors + [name]    
        # for each node in the network evaluate if there is a shorter path to that node from self router neighbors. 
        for node in self.N:
            for neighbor in self.neighbors:
                if neighbor in self.R: # if node is a router
                    # collect variables for equation for each y in N: D x (y) = min v {c(x, v) + D v (y)}
                    D_to_node_from_self = table[node][name] #current cost
                    #sum of next two variables is new possible cost
                    cost_to_neighbor = self.cost_D[neighbor][next(iter(self.cost_D[neighbor]))]
                    D_to_node_from_neighbor = table[node][neighbor] 
                    #select the minimum of the two
                    new_Distance = min(D_to_node_from_self, cost_to_neighbor + D_to_node_from_neighbor)
                    # if the cost has changed, update routing table
                    #if D_to_node_from_self > new_Distance:
                    self.rt_tbl_D[node][name] = new_Distance
        self.print_routes()

        # compare the new distance vector and send updated vector to neighbors if new
        new_distance_vector = {}
        for node in self.N:
            cost_to_node = self.rt_tbl_D[node][self.name]
            new_distance_vector.update({node: {self.name: cost_to_node}})
        
        if new_distance_vector != current_distance_vector:
            for neighbor in self.neighbors: 
                self.send_routes(next(iter(self.cost_D[neighbor])))

        print('%s: Received routing update %s from interface %d' % (self, p, i))

                
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.process_queues()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 