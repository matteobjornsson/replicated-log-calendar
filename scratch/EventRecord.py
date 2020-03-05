
class EventRecord:
    operation = ""
    appointment = None
    time = 0
    node = 0
    iterable = None
    stringRepresentation = ""
    #String Represenatation: "TIME  NODEID  OPERATION  APPOINTMENTNAME DAY START END PARTICIPANTS" #

    def __init__(self, operation: str, appointment: tuple, time: int,
                nodeID: int):

            self.operation = operation 
            self.appointment = appointment
            self.time = time
            self.node = nodeID
            self.iterable = [
                time,
                nodeID,
                operation,
                appointment[0],      # APPOINTMENT NAME
                str(appointment[1]), # DAY   
                str(appointment[2]), # START
                str(appointment[3]), # END
                str(appointment[4])  # PARTICIPANTS 
            ]
            self.stringRepresentation = (str(time) + '\t'   # TIME 
                                    + str(nodeID) + '\t'    # NODEID
                                    + operation + '\t'      # OPERATION
                                    + appointment[0] + '\t'       # APPOINTMENTNAME
                                    + str(appointment[1]) + '\t'  # DAY   
                                    + str(appointment[2]) + '\t'  # START
                                    + str(appointment[3]) + '\t'  # END
                                    + str(appointment[4]))        # PARTICIPANTS
    
    def printEventRecord(self):
        print(self.stringRepresentation)

