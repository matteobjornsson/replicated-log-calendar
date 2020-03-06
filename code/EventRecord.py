

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
            self.stringRepresentation = (
                  str(time) + '\t'                # TIME 
                + str(nodeID) + '\t'            # NODEID
                + operation + '\t'              # OPERATION
                + appointment[0] + '\t'         # APPOINTMENTNAME
                + str(appointment[1]) + '\t'    # DAY   
                + str(appointment[2]) + '\t'    # START
                + str(appointment[3]) + '\t'    # END
                + str(appointment[4])           # PARTICIPANTS
                )        
    
    def printEventRecord(self):
        print(self.stringRepresentation)

if __name__ == '__main__':
    doctorAppointment = ("Doctor Appointment", 2, 12.5, 13.5, [1,2])
    dmvAppointment = ("DMV", 5, 12.5, 13.5, [4])
    siingAppointment = ("Skiing", 7, 8, 18, [2,3])

    eR1 = EventRecord("Insert", doctorAppointment, 2, 3)
    eR2 = EventRecord("Insert", dmvAppointment, 3, 3)
    print(eR1.stringRepresentation)
    print(eR1.iterable)

'''
#prior attempt to make an immutable object:

from dataclasses import dataclass

@dataclass(frozen=True)
class EventRecord:
    event: str
    time: int
    node: int
'''