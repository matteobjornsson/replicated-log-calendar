import pickle

class wuuCalendar:

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