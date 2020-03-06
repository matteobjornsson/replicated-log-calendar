import pickle

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

    appointments = {}
    calendarFile = None

    def __init__(self):
        self.updateCalendarFile() # right now calendar writes a new file instead of checking for one

    def insertAppointment(self, appointment: tuple) -> None: 
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
        self.appointments[appointment[0]] = appointment
        self.updateCalendarFile()

    def deleteAppointment(self, appointmentName: str) -> None:
        del self.appointments[appointmentName]
        self.updateCalendarFile()

    def updateCalendarFile(self) -> None:
        with open('../files/calendar.pickle', 'wb') as calendarFile:
            pickle.dump(self.appointments, calendarFile)

    def printCalendar(self) -> None:
        with open('../files/calendar.pickle', 'rb') as calendarFile:
            unpickledCalendar = pickle.load(calendarFile)
        print(unpickledCalendar)

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


