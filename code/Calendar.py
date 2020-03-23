import pickle, os

class CalendarConflictError(ValueError):
    '''Raise error when a conflicting appointment occurs'''
    def __init__(self, message):
        self.message = message

class Calendar:
    '''
    Class for storing and manipulating appointments generated by Node user

    Attributes:
        appointments
        calendarFile

    Methods: 
        __init__()
        insertAppointment(appointment)
        deleteAppointment(appointmentName)
        updateCalendarFile()
        printCalendar()
        
    '''
    calendarFile = None

    def __init__(self, nodeID, appointments = {}):
        #self.appointments = {}
        if not os.path.isdir('../files'):
            os.mkdir('../files')  
        #file_path = '../files/logOutput.tsv'
        filename = "calendar" + str(nodeID) + ".pkl"
        self.file_path = '../files/' + filename
        try:
            read_file = open(self.file_path, 'rb')
            self.appointments = pickle.load(read_file)
            read_file.close()
        except FileNotFoundError:
            self.appointments = appointments
            print("No calendar object available to read in")
        self.updateCalendarFile() 

    def insertAppointment(self, appointment: tuple, override = False) -> None: 
        '''
        @param appointment = (
            name: str, 
            day: int, 
            start_time: float, 
            end_time: float, 
            participants: list
            )
        type: tuple
        '''

        #create date tuple for incoming appointment
        incoming_appt_date = (appointment[1], appointment[2], appointment[3])

        #If override == False, i.e., the incoming appt needs to be checked for conflicts 
        #   iterate over all existing appointments in current calendar
        if not override:
            # TODO: I think we need to change this logic so that check date conflict
            # automatically checks all in log given incoming date, returns boolean. 
            if self.check_participants_overlap(appointment[4]):
                if self.check_date_conflict(incoming_appt_date):
                    raise CalendarConflictError("Conflicting appointments occurred")
                       
            self.appointments[appointment[0]] = appointment
            self.updateCalendarFile()
        else:
            self.appointments[appointment[0]] = appointment
            self.updateCalendarFile()
    
    def check_participants_overlap(self, incoming_participants):
        for appt_name, appt in self.appointments.items():
            existing_participants = appt[4]
            if not set(existing_participants).isdisjoint(incoming_participants):
                return True
            else:
                return False
        
    def check_date_conflict(self, incoming_date):
        """
        Checks for date conflict, each date is a tuple of the form: (date, starttime, endtime)
        """
        #Check if event is on the same day
        for appt_name, appt in self.appointments.items():
            existing_date = (appt[1], appt[2], appt[3])
            if existing_date[0] == incoming_date[0]:
                #Check if it starts at the same time
                if existing_date[1] == incoming_date[1]:
                    return True
                #Check if it ends at the same time
                elif existing_date[2] == incoming_date[2]:
                    return True
                #Check if there is overlap in start/end time
                elif max(0, min(existing_date[2], incoming_date[2]) - max(existing_date[1], incoming_date[1])) > 0:
                    return True
                else:
                    return False
            else:
                return False

    def deleteAppointment(self, appointmentName: str) -> None:
        del self.appointments[appointmentName]
        self.updateCalendarFile()
        # TODO: check for existing delete

    def updateCalendarFile(self) -> None:
        calendarFile = open(self.file_path, 'wb')
        pickle.dump(self.appointments, calendarFile)
        calendarFile.close()


    def printCalendar(self) -> None:
        #with open('../files/calendar.pickle', 'rb') as calendarFile:
        #    unpickledCalendar = pickle.load(calendarFile)
        print(self.appointments)

    def contains(self, appointmentName: str) -> bool:
        return (appointmentName in self.appointments)

    def getAppointment(self, appointmentName: str) -> tuple:
        return self.appointments[appointmentName]


if __name__ == '__main__':
    # Testing... Testing..... 
    cal = Calendar()
    doctorAppointment = ("Doctor Appointment", 2, 12.5, 13.5, [1,2])
    cal.insertAppointment(doctorAppointment)
    cal.insertAppointment(("DMV", 5, 12.5, 13.5, [4]))
    cal.insertAppointment(("Skiing", 7, 8, 18, [2,3]))
    cal.printCalendar()
    cal.deleteAppointment("DMV")
    cal.printCalendar()


