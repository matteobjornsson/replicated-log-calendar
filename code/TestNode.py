import Node
import argparse, pickle

parser =  argparse.ArgumentParser(description='Node instance')
parser.add_argument('nodeID', help='NodeID.', type=int)
args = parser.parse_args()
node = Node.Node(4, args.nodeID)
"""
try:
    read_file = open('incoming2.pkl', 'rb')
    incomingMessage = pickle.load(read_file)
    read_file.close()
except FileNotFoundError:
    print("No incoming message available to read in")

incomingNPLog = incomingMessage[0]
incomingNPTimeTable = incomingMessage[1]
node.receive(incomingNPLog, incomingNPTimeTable)
node.displayCalendar()
print(node.timeTable)
"""