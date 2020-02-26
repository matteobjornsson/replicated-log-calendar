import numpy as np


class DistributedDictionary:
    timeTable = None    # Two dimensional time table
    localDictionary = None    # local copy of dictionary
    partialLog = None   # Partial Log of insert and delete events. TODO: what datastructure should this be?
    id = None   # node id

    def __init__(self, N: int, i: int):
        self.timeTable = np.zeros( (N, N) )
        self.id = i

    def updateClock(self, clockTime: int) -> void:
        timeTable[id][id] = clockTime

    def hasrec(self, timeTable: TwoDimensionalTimeTable, eR: eventRecord, targetNode: int)-> bool:
        # true if T[targetNode][eR.node] >= eR.time

class EventRecord:
    event = ""
    time = None
    node = None

    def __init__(self, event: str, time: int, node: int) -> void:
        self.event = event
        self.time = time
        self.node = node


class Log:
    eventLog = np.array([]) #initialize empty array? is this be best datastructure? 

    def __init__(self):
        # constructor here
    
    def insert(self, eR: EventRecord) -> void:
        #method here

    def delete(self, eR: EventRecord) -> void:
        #method here

    def contains(self, eR: EventRecord) -> bool: 
        #method here