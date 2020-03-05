import wuuCalendar as Calendar
import Log
import numpy

class WuuNode:

    lamportClock = 0
    calendar = Calendar.Calendar()
    timeTable = None
    log = None
    nodeID = 0


    ## constructor: 

    def __init__(self, N: int, i: int):
        self.timeTable = numpy.zeros((N,N))
        self.nodeID = i


    ## clock:
    def clock(self) -> int:
        self.lamportClock += 1
        return self.lamportClock

    ## insert
    def insertEvent(self, appointment: tuple):
        print("I\'ve inserted an appointment")
        # time = self.clock()
        # timeTable[nodeID][nodeID] = time
        # eR = EventRecord("Insert", appointment, time, self.nodeID)
        # log.insertRecord(eR)
        # calendar.insertEvent(appointment)

    ## delete
    def deleteEvent(self, appointmentName: str):
        print('I\'ve deleted appointment: {}'.format(appointmentName))
        # time = self.clock()
        # timeTable[nodeID][nodeID] = time
        # eR = EventRecord("Delete", appointmentName, time, self.nodeID)
        # log.insertRecord(eR)
        # calendar.deleteEvent(appointmentName)
    
    ## Build Partial Log to Send
    # def buildPartialLog(self, targetNode: int) 



#class PartialLog:

