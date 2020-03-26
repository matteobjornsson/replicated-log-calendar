import Node
import argparse, pickle, threading
from time import sleep

parser =  argparse.ArgumentParser(description='Node instance number (1-4)')
parser.add_argument('nodeID', help='NodeID.', type=int)
args = parser.parse_args()
node = Node.Node(4, args.nodeID)

## appointments for test purposes:
choice5 = ("DMV", 3, 12.5, 13.5, [1,2,3])
choice6 = ("Skiing", 3, 6.0, 17.0, [3])
###

def check_refresh():
    while True:
        if node.refresh_calendar:
            node.displayCalendar()
            print(
                "What action would you like to perform? \n\t1. Insert "
                + "appointment \n\t2. Delete appointment \n\t3. Refresh "
                + "calendar \n\t4. Exit calendar application\n"
            )
        sleep(.5)


threading.Thread(
    target=check_refresh, 
    daemon=True
).start()

running_calendar = True
print("Welcome! \n Here is your current calendar:\n")
node.displayCalendar()
while running_calendar:
    print(
        "What action would you like to perform? \n\t1. Insert "
        + "appointment \n\t2. Delete appointment \n\t3. Refresh "
        + "calendar \n\t4. Exit calendar application\n"
    )
    user_choice = input()
    try:
        user_choice = int(user_choice)
    except ValueError:
        print("Not a valid input, try again.")
    
    if user_choice == 1:
        node.addCalendarAppointment()
        node.displayCalendar()
    elif user_choice == 2:
        node.deleteCalendarAppointment()
        node.displayCalendar()
    elif user_choice == 3:
        node.displayCalendar()
    elif user_choice == 4:
        print("\nI hope your calendar is up to date. Enjoy the rest of your week.")
        running_calendar = False

    #### options for testing: 
    elif user_choice == 5:
        node.addCalendarAppointment(choice5)
        node.displayCalendar()
    elif user_choice == 6:
        node.addCalendarAppointment(choice6)
        node.displayCalendar()
    ####
    
    else:
        "Not a valid choice, please enter 1,2,3, or 4."


