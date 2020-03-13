import Calendar
import Log
#import PartialLog
import EventRecord as ER
import numpy
import Messenger
import pickle
import argparse

class Node:

## constructor: 

    def __init__(self, N: int, i: int):
        self.lamportTime = 0
        self.timeTable = numpy.zeros((N,N))
        self.nodeID = i
        self.log = Log.Log() 
        self.calendar = Calendar.Calendar() 
        self.messenger = Messenger.Messenger(i)

## clock:
    def clock(self) -> int:
        self.lamportTime += 1
        return self.lamportTime

## message proccessing: 

    def receive(self, received_NP_log, received_timetable):
        # TODO: who is sender for TT update?
        received_nodeID = 0
        for eventRecordFromNP in received_NP_log:
            #Create list of new eventrecords to update log later
            # (if time of incoming event time is newer (greater than) our 
            # TimeTable record of that node time append record to our log)
            if not self.hasRec(eventRecordFromNP, self.nodeID):  #Create list of new eventrecords to update log later
                self.log.insert(eventRecordFromNP)
            if eventRecordFromNP.operation == "Insert": #Update calendar object when inserting
                #if received_nodeID == 0:
                #    received_nodeID = eventRecordFromNP.nodeID
                """
                Check if current node is participant in event, if yes: there may be conflicts!
                If not, you can simply insert the event.
                """
                if self.nodeID in eventRecordFromNP.appointment[4]:
                    try:
                        self.calendar.insertAppointment(eventRecordFromNP.appointment) #Check for conflict resolution
                    except ValueError:
                        #Tiebreaker based on node id's, higher node id wins the insert right. New event is being inserted.
                        if received_nodeID > self.nodeID:   
                            self.calendar.insertAppointment(eventRecordFromNP.appointment, override=True) #Currently overriding calendar appt, TODO: not doing anything with log eventrecords!
                            
                        #Existing event wins, incoming event is "ignored", i.e. a delete has to be sent.
                        else: 
                            print("Appointment was not inserted because there is a conflict. Incoming event is being deleted.")
                            #SEND DELETE TO NODES
                else:
                    self.calendar.insertAppointment(eventRecordFromNP.appointment, override=True)
            elif eventRecordFromNP.operation == "Delete": #Update calendar object when deleting
                self.calendar.deleteAppointment(eventRecordFromNP.appointment[0])

        for i in range(len(self.timeTable[0])): #Update timetable
            self.timeTable[self.nodeID-1][i] = max(self.timeTable[self.nodeID-1][i], received_timetable[received_nodeID-1][i])
            for j in range(len(self.timeTable[0])):
                self.timeTable[i][j] = max(self.timeTable[i][j], received_timetable[i][j])
        
        #self.log = [[er for er in self.log if not self.hasRec(er, j)] 
        #           for j in range(len(self.timeTable[0]))]
        #TODO: we need to be using log.insert() so it gets written to file instead of appending directly to log attribute
        updated_log = []
        for er in self.log.log:
            for j in range(len(self.timeTable[0])):
                if not self.hasRec(er, j):
                    updated_log.append(er)
        self.log = updated_log

        # process incoming messages. Update the timeTable and calendar accordingly. 
        # options:  add appointment
        #           delete appointment
        # add any appointments to the log by passing an eventRecord object to 
        # addEventToLog()

    def send(self, to_nodeId):
        """
        message to be sent
        """
        NP = [eR for eR in self.log.log if not self.hasRec(eR, to_nodeId)]
        message = (NP, self.timeTable)
        self.messenger.send(to_nodeId, message)

        ''' This is for testing: 
        printableNP = []
        for eR in NP:
            printableNP.append(eR.stringRepresentation)
        print([printableNP, self.timeTable])

        message = open('incoming2.pkl', 'wb')
        pickle.dump((NP, self.timeTable), message)
        message.close()
        '''

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
        self.timeTable[self.nodeID-1][self.nodeID-1] = lamportTime
        eR = ER.EventRecord("Insert", appointment, lamportTime, self.nodeID)
        self.log.insert(eR)
        try:
            self.calendar.insertAppointment(appointment)
        except ValueError:
            print("Appointment already exists.")
            confirm_update = input(
                "Would you like to override the existing appointment? (y/n)"
                )
            if confirm_update == "y":
                self.calendar.insertAppointment(appointment, override = True)
        print("\"{}\" added to calendar.".format(appointment[0]))


    def deleteCalendarAppointment(self):
        appointmentName = input(
            "Enter the exact text of the appointment name you wish to delete: "
            )
        if self.calendar.contains(appointmentName):
            lamportTime = self.clock()
            self.timeTable[self.nodeID-1][self.nodeID-1] = lamportTime
            eR = ER.EventRecord(
                "Delete", 
                self.calendar.getAppointment(appointmentName), 
                lamportTime, 
                self.nodeID
            )
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

    def hasRec(self, eR, otherNodeId: int):
        if self.timeTable[otherNodeId-1][eR.nodeID-1] >= eR.lamportTime:
            return True
        else:
            return False


if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='Node instance')
    parser.add_argument('nodeID', help='NodeID.', type=int)
    args = parser.parse_args()

    node = Node(4, args.nodeID)
    doctorAppointment = ("Dentist Appointment", 1, 12.5, 13.5, [1,2])
    dmvAppointment = ("DeeMVee", 5, 12.5, 13.5, [1,2])
    newAppointment = ("NewAppt", 6, 20.0, 22.0, [2,4])

    node.addCalendarAppointment(doctorAppointment)
    node.addCalendarAppointment(dmvAppointment)

    # node.addCalendarAppointment()
    node.displayCalendar()
    node.deleteCalendarAppointment()
    node.addCalendarAppointment(newAppointment)
    node.displayCalendar()

    print(node.timeTable)

    node.send(3)

    try:

        read_file = open('incoming1.pkl', 'rb')

        incomingMessage = pickle.load(read_file)
        read_file.close()
    except FileNotFoundError:
        print("No incoming message available to read in")
    
    incomingNPLog = incomingMessage[0]
    incomingNPTimeTable = incomingMessage[1]
    node.receive(incomingNPLog, incomingNPTimeTable)
    node.displayCalendar()
    print(node.timeTable)

" Test Objects :" 
'''
time table at the end of main:

self.timeTable = 
[[0. 0. 0. 0.]
 [0. 0. 0. 0.]
 [0. 0. 4. 0.]
 [0. 0. 0. 0.]]
'''


