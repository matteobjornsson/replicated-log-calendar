import Calendar
#import LogProcessor
#import PartialLog
#import EventRecord
import numpy

class Node:

    lamportClock = 0
    # right now calendar writes a new file instead of checking for one
    calendar = Calendar.Calendar() 
    timeTable = None
    log = None 
    nodeID = None
#   logProcessor = LogProcessor #not sure if this should be instantiated here 
#   or in the methods that would use it. 

## constructor: 

    def __init__(self, N: int, i: int):
        self.timeTable = numpy.zeros((N,N))
        self.nodeID = i

## clock:
    def clock(self) -> int:
        self.lamportClock += 1
        return self.lamportClock

## message proccessing: 

#    def receive(self, m: message) -> void:
        # process incoming messages. Update the timeTable and calendar accordingly. 
        # options:  add event
        #           delete event
        # add any events to the log by passing an eventRecord object to addEventToLog()

#    def send(self, m: message) -> void:
        # send a message to other nodes when a change is made to the log
        # or as required to resolve conflicts. 
        # Use logProcessor to buld a PartialLog with hasrec() to include with message. 

#    def addEventToLog(self, eR: EventRecord) -> void:
        # use logProcessor object to add record to text file. 

#    def updateTimeTable(self):
        # helper method for receive(), should include add'l parameters


## User interaction: 

    def addCalendarEvent(self):
        name = input("Enter the name of the appointment: ")
        day = input("Enter the day of the appointment: \n \
                    Sunday: 1 \n \
                    Monday: 2 \n \
                    Tuesday: 3 \n \
                    Wednesday: 4 \n \
                    Thursday: 5 \n \
                    Friday: 6 \n \
                    Saturday: 7 \n")
        start_time = input("Enter the start time of the appointment. " +\
            "Use 24hr time, falling on the hour or half hour " +\
            "(e.g 8:00AM -> 8.0, 5:30pm -> 17.5): ")
        
        end_time = input("Enter the start time of the appointment :")
        participants = input("Enter the ID numbers of all participants, \
                separated by commas (e.g. 1, 3, 4): \n\n")
        
        self.calendar.insertEvent(name, day, start_time, end_time, participants)

        print("\"{}\" added to calendar.".format(name))


    def deleteCalendarEvent(self):
        eventName = input("Enter event name (exact text): ")
        self.calendar.deleteEvent(eventName)
        print("\"{}\" event deleted.\n".format(eventName))

    def displayCalendar(self): 
        self.calendar.printCalendar()

# These methods are the same as above but built to take the information 
# directly as parameters, 

    def testAddCalendarEvent(self, name: str, day: int, start_time: float, 
                                end_time: float, participants: list) -> None:
        self.calendar.insertEvent(name, day, start_time, end_time, participants)

    def testDeleteCalendarEvent(self, eventName: str) -> None:
        self.calendar.deleteEvent(eventName)


if __name__ == '__main__':
    node = Node(4, 1)
    node.addCalendarEvent()
    node.addCalendarEvent()
    node.displayCalendar()
    node.deleteCalendarEvent()
    node.displayCalendar()
