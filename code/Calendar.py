import pickle

class CalendarConflictError(ValueError):
    '''Raise error when a conflicting appointment occurs'''
    def __init__(self, message):
        self.message = message

class Calendar:
    '''
    put the class header here

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

    def __init__(self, appointments = {}):
        #self.appointments = {}
        try:
            read_file = open('../files/calendar.pkl', 'rb')
            self.appointments = pickle.load(read_file)
            print("pickle: ",self.appointments)
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
        print(self.appointments)
        if appointment[0] in self.appointments.keys() and not override:
            raise CalendarConflictError("Conflicting appointments occurred")
        else:
            self.appointments[appointment[0]] = appointment
            self.updateCalendarFile()

    def deleteAppointment(self, appointmentName: str) -> None:
        del self.appointments[appointmentName]
        self.updateCalendarFile()

    def updateCalendarFile(self) -> None:
        calendarFile = open('../files/calendar.pkl', 'wb')
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


