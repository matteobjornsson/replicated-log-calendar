import pickle

class Calendar:

    events = {}
    calendarFile = None

    def __init__(self):
        self.updateCalendarFile() # right now calendar writes a new file instead of checking for one

    def insertEvent(self, name: str, day: int, start_time: float, \
        end_time: float, participants: list) -> None: 

        event = (name, day, start_time, end_time, participants)
        self.events[event[0]] = event
        self.updateCalendarFile()

    def deleteEvent(self, eventName: str) -> None:
        del self.events[eventName]
        self.updateCalendarFile()

    def updateCalendarFile(self) -> None:
        with open('../files/calendar.pickle', 'wb') as calendarFile:
            pickle.dump(self.events, calendarFile)

    def printCalendar(self) -> None:
        with open('../files/calendar.pickle', 'rb') as calendarFile:
            unpickledCalendar = pickle.load(calendarFile)
        print(unpickledCalendar)

if __name__ == '__main__':
    # Testing... Testing..... 
    cal = Calendar()
    cal.insertEvent("Doctor Appointment", 2, 12.5, 13.5, [1,2])
    cal.insertEvent("DMV", 5, 12.5, 13.5, [4])
    cal.insertEvent("Skiing", 7, 8, 18, [2,3])
    cal.printCalendar()
    cal.deleteEvent("DMV")
    cal.printCalendar()


