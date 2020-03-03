import scratch.wuuCalendar as Calendar
import scratch.Log as Log
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
    def insertEvent(self, event: tuple):
        print("I\'ve inserted an event")
        # time = self.clock()
        # timeTable[nodeID][nodeID] = time
        # eR = EventRecord("Insert", event, time, self.nodeID)
        # log.insertRecord(eR)
        # calendar.insertEvent(event)

    ## delete
    def deleteEvent(self, eventName: str):
        print('I\'ve deleted event: {}'.format(eventName))
        # time = self.clock()
        # timeTable[nodeID][nodeID] = time
        # eR = EventRecord("Delete", eventName, time, self.nodeID)
        # log.insertRecord(eR)
        # calendar.deleteEvent(eventName)
    
    ## Build Partial Log to Send
    # def buildPartialLog(self, targetNode: int) 


class EventRecord:
    operation = ""
    event = None
    time = 0
    node = 0
    stringRepresentation = ""

    def __init__(self, operation: str, event: str or tuple, time: int,
                nodeID: int):

        if isinstance(event, tuple):
            self.operation = operation 
            self.event = event
            self.time = time
            self.node = nodeID
            self.stringRepresentation = operation + ": Event Name: " + event[0] \
                + " Day: " + str(event[1]) + " Start Time: " + str(event[2]) \
                + " End Time: " + str(event[3]) + "Participants: " \
                + str(event[4])
        
        elif isinstance(event, str):
            self.operation = operation 
            self.event = event
            self.time = time
            self.node = nodeID
            self.stringRepresentation = operation + ": Event Name: " + event
    
    def printEventRecord(self):
        print(self.stringRepresentation)



#class PartialLog:

