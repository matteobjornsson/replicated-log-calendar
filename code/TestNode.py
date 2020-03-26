import Node
import argparse, pickle

parser =  argparse.ArgumentParser(description='Node instance')
parser.add_argument('nodeID', help='NodeID.', type=int)
args = parser.parse_args()
node = Node.Node(4, args.nodeID, 1)

running_calendar = True
print("Welcome! \n Here is your current calendar:\n")
node.displayCalendar()
while running_calendar:
    print("What action would you like to perform? \n\t1. Insert appointment \n\t2. Delete appointment \n\t3. Refresh calendar \n\t4. Exit calendar application\n")
    user_choice = input()
    try:
        user_choice = int(user_choice)
    except ValueError:
        print("Not a valid input, try again.")
    
    if user_choice == 1:
        node.addCalendarAppointment()
    elif user_choice == 2:
        node.deleteCalendarAppointment()
    elif user_choice == 3:
        node.displayCalendar()
    elif user_choice == 4:
        print("\nI hope your calendar is up to date. Enjoy the rest of your week.")
        running_calendar = False
    else:
        "Not a valid choice, please enter 1,2,3, or 4."
