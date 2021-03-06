

class EventRecord:
    '''
    This class holds all arguments needed to record events to a distributed log.

    These records are for implementing a distributed calendar, thus also store
    Appointment information as well as operations. They have attributes inteded
    to support storing in a tsv file.

    Attributes:
        operation (string):     Operation type, e.g. "Insert" or "Delete"
        appointment (tuple):    Calendar appointment, must consist of a tuple 
                                    (name: str, day: int, start_time: float, 
                                    end_time: float, participants: List)
        lamportTime (int):      Number representing event order on parent node
        node (int):             ID of the parent node the event occured on
        iterable (List):        An iterable form of the record
        stringRepresentation (str): A string representation of the record
                                in tab separated format (to append to log):
                    "TIME \t NODEID \t OPERATION \t APPOINTMENTNAME \t DAY \t 
                    START \t END \t PARTICIPANTS"

    For reference, an event record as defined in Wuu and Bernstein:
    type Event = 
        record
            op  :   OperationType;
            time:   TimeType;
            node:   NodeId;
        end

    '''
    
    def __init__(self, operation: str, appointment: tuple, lamportTime: int,
                nodeID: int):
        """
        The constructor for the EventRecord Class
        
        Parameters:
            operation (str):        Operation, e.g. "Insert" or "Delete"
            appointment (tuple):    Calendar Appointment subject to operation
            lamportime (int):      event order on parent node
            nodeID (int):           parent node ID 
        """

        self.operation = operation 
        self.appointment = appointment
        self.lamportTime = lamportTime
        self.nodeID = nodeID
        self.iterable = [
            lamportTime,
            nodeID,
            operation,
            appointment[0],      # APPOINTMENT NAME
            str(appointment[1]), # DAY   
            str(appointment[2]), # START
            str(appointment[3]), # END
            str(appointment[4])  # PARTICIPANTS 
        ]
        self.stringRepresentation = (
            
              str(lamportTime) + '\t'       # TIME 
            + str(nodeID) + '\t'            # NODEID
            + operation + '\t'              # OPERATION
            + appointment[0] + '\t'         # APPOINTMENTNAME
            + str(appointment[1]) + '\t'    # DAY   
            + str(appointment[2]) + '\t'    # START
            + str(appointment[3]) + '\t'    # END
            + str(appointment[4])           # PARTICIPANTS
            )        
    
    def printEventRecord(self):
        """
        method to print out an event record. 
        """
        print(self.stringRepresentation)
    
    def __eq__(self, other):
        """
        Overriding equals method to perform checks between eventrecord objects in the log.
        """
        if other.operation == self.operation: #Check if operation is the same, because that is the first check that matters
            if other.operation == "Insert": #If event is Inserting an appt, check all other attributes
                if self.lamportTime == other.lamportTime and self.nodeID == other.nodeID and self.appointment[0] == other.appointment[0]: #appt[0] represents appt name, as names are unique this is all that matters
                    return True
                else:
                    return False
            else: #If deleting event, all that matter is the appt name (appt[0])
                if self.appointment[0] == other.appointment[0]:
                    return True
                else:
                    return False       


if __name__ == '__main__':
    #TESTING
    doctorAppointment = ("Doctor Appointment", 2, 12.5, 13.5, [1,2])
    dmvAppointment = ("DMV", 5, 12.5, 13.5, [4])
    siingAppointment = ("Skiing", 7, 8, 18, [2,3])

    eR1 = EventRecord("Insert", doctorAppointment, 2, 3)
    eR2 = EventRecord("Insert", dmvAppointment, 3, 3)
    print(eR1.stringRepresentation)
    print(eR1.iterable)