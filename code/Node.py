import Calendar
import Log
#import PartialLog
import EventRecord as ER
import numpy
import Messenger

class Node:

#   logProcessor = LogProcessor #not sure if this should be instantiated here 
#   or in the methods that would use it. 

## constructor: 

    def __init__(self, N: int, i: int, nodesToConnectTo: list):
        self.lamportTime = 0
        self.timeTable = numpy.zeros((N,N))
        self.nodeID = i
        self.log = Log.Log() 
        self.calendar = Calendar.Calendar() 
        self.messenger = Messenger.Messenger()

## clock:
    def clock(self) -> int:
        self.lamportClock += 1
        return self.lamportClock

## message proccessing: 

#    def receive(self, m: message) -> void:
        # process incoming messages. Update the timeTable and calendar accordingly. 
        # options:  add appointment
        #           delete appointment
        # add any appointments to the log by passing an eventRecord object to addEventToLog()

#    def send(self, m: message) -> void:
        # send a message to other nodes when a change is made to the log
        # or as required to resolve conflicts. 
        # Use logProcessor to buld a PartialLog with hasrec() to include with message. 

#    def addEventToLog(self, eR: EventRecord) -> void:
        # use logProcessor object to add record to text file. 

#    def updateTimeTable(self):
        # helper method for receive(), should include add'l parameters


## User interaction logic: 

    def addCalendarAppointment(self, appointment = None):
        if appointment == None:
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
            
            appointment = (name, day, start_time, end_time, participants)
        
        lamportTime = self.clock()
        self.timeTable[self.nodeID][self.nodeID] = lamportTime
        eR = ER.EventRecord("Insert", appointment, lamportTime, self.nodeID)
        self.log.insert(eR)
        self.calendar.insertAppointment(appointment)
        print("\"{}\" added to calendar.".format(appointment[0]))


    def deleteCalendarAppointment(self):
        appointmentName = input(
            "Enter the exact text of the appointment name you wish to delete: "
            )
        if self.calendar.contains(appointmentName):
            lamportTime = self.clock()
            self.timeTable[self.nodeID][self.nodeID] = lamportTime
            eR = ER.EventRecord("Delete", self.calendar.getAppointment(appointmentName), lamportTime, self.nodeID)
            self.log.insert(eR)
            self.calendar.deleteAppointment(appointmentName)
            print("\"{}\" appointment deleted.\n".format(appointmentName))
        else:
            print("\"{}\" not in calendar".format(appointmentName))


    def displayCalendar(self): 
        self.calendar.printCalendar()

# These methods are the same as above but built to take the information 
# directly as parameters, 

    def testAddCalendarAppointment(self, appointment: tuple) -> None:
        self.calendar.insertAppointment(appointment)

    def testDeleteCalendarAppointment(self, appointmentName: str) -> None:
        self.calendar.deleteAppointment(appointmentName)

    def hasRec(self, eR: eventRecord, otherNodeId: int):
        if self.timeTable[otherNodeId, eR.nodeID] >= eR.lamportTime:
            return True
        else:
            return False


if __name__ == '__main__':
    node = Node(4, 1)
    doctorAppointment = ("Doctor Appointment", 2, 12.5, 13.5, [1,2])
    dmvAppointment = ("DMV", 4, 12.5, 13.5, [1,2])
    node.addCalendarAppointment(doctorAppointment)
    node.addCalendarAppointment(dmvAppointment)
    # node.addCalendarAppointment()
    # node.addCalendarAppointment()
    node.displayCalendar()
    node.deleteCalendarAppointment()
    node.displayCalendar()
    

