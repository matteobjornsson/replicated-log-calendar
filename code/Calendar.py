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

    def __init__(self, nodeID, freshBoot: bool):
        self.appointments = {}
        if not os.path.isdir('../files'):
            os.mkdir('../files')  
        #file_path = '../files/logOutput.tsv'
        filename = "calendar" + str(nodeID) + ".pkl"
        self.file_path = '../files/' + filename
        if not freshBoot:
            try:
                read_file = open(self.file_path, 'rb')
                self.appointments = pickle.load(read_file)
                read_file.close()
            except FileNotFoundError:
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
            print("override = false")
            if self.check_participants_overlap(appointment[4]):
                print("participant overlap occurred")
                if self.check_date_conflict(incoming_appt_date):
                    print("date conflict occurred")
                    raise CalendarConflictError("Conflicting appointments occurred")
                else:
                    print("no date overlap")
                    self.appointments[appointment[0]] = appointment
                    self.updateCalendarFile()
            else:
                print("no participant overlap")
                self.appointments[appointment[0]] = appointment
                self.updateCalendarFile()
                    
        elif override:
            self.appointments[appointment[0]] = appointment
            self.updateCalendarFile()
    
    def check_participants_overlap(self, incoming_participants):
        """

        """
        for appt_name, appt in self.appointments.items():
            existing_participants = appt[4]
            print("existing: ", set(existing_participants))
            print("incoming: ", set(incoming_participants))
            if existing_participants == incoming_participants:
                print("exact same participants")
                return True
            elif not set(existing_participants).isdisjoint(set(incoming_participants)):
                print("overlapping participants")
                return True

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
        return False

    def deleteAppointment(self, appointmentName: str) -> None:
        try:
            del self.appointments[appointmentName]
            self.updateCalendarFile()
        except KeyError:
            print("Appointment does not exist in calendar.")

        # TODO: check for existing delete

    def updateCalendarFile(self) -> None:
        calendarFile = open(self.file_path, 'wb')
        pickle.dump(self.appointments, calendarFile)
        calendarFile.close()


    def printCalendar(self) -> None:
        #with open('../files/calendar.pickle', 'rb') as calendarFile:
        #    unpickledCalendar = pickle.load(calendarFile)
        print('\nCalendar: ')
        for appointmentName, appointment in self.appointments.items():
            print(appointment)

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


