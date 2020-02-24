import Calendar
import LogProcessor
import PartialLog
import EventRecord
import numpy

class Node:

    lamportClock = 0
    calendar = Calendar()
    timeTable = None
    log = None 
    nodeID = None
    logProcessor = LogProcessor #not sure if this should be instantiated here or in the methods that would use it. 

## constructor: 

def __init__(self, N: int, i: int):
    self.timeTable = numpy.zeros((N,N))
    self.nodeID = i

## message proccessing: 

def receive(self, m: message) -> void:
    # process incoming messages. Update the timeTable and calendar accordingly. 
    # options:  add event
    #           delete event
    # add any events to the log by passing an eventRecord object to addEventToLog()

def send(self, m: message) -> void:
    # send a message to other nodes when a change is made to the log
    # or as required to resolve conflicts. 
    # Use logProcessor to buld a PartialLog with hasrec() to include with message. 

def addEventToLog(self, eR: EventRecord) -> void:
    # use logProcessor object to add record to text file. 

def updateTimeTable(self):
    # helper method for receive(), should include add'l parameters


## User interaction: 

def addCalendarEvent(self):
    # Method for user to add event

def deleteCalendarEvent(self):
    # Method for user to delete event

def displayCalendar(self): 
    # method to display calendar to user. 
