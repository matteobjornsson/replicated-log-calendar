import Node
import argparse, pickle

parser =  argparse.ArgumentParser(description='Node instance')
parser.add_argument('nodeID', help='NodeID.', type=int)
args = parser.parse_args()
node = Node.Node(4, args.nodeID, 1)

running_calendar = True

while running_calendar:
    print("Welcome! \n ")
    userChoice = input("What action would you like to perform? \n\t1. View calendar \n\t2. Insert appointment \n\t3. Delete appointment")
    try:
        ins_del_bool = int(userChoice)
    except ValueError:
        "Not a valid input, try again."
    
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