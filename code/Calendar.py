import pickle, os
import numpy as np

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
                date_overlap_bool, name_of_event = self.check_date_conflict(incoming_appt_date)
                if date_overlap_bool:
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
    
    def get_conflicting_appt_name(self, appointment):
        incoming_appt_date = (appointment[1], appointment[2], appointment[3])
        if self.check_participants_overlap(appointment[4]):
                date_overlap_bool, name_of_event = self.check_date_conflict(incoming_appt_date)
                if date_overlap_bool:
                    #self.appointments[appointment[0]] = appointment
                    #self.updateCalendarFile()
                    return name_of_event

    def check_participants_overlap(self, incoming_participants):
        """
        Check if there is overlap in the participants lists of the appointments
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
                    return True, appt_name
                #Check if it ends at the same time
                elif existing_date[2] == incoming_date[2]:
                    return True, appt_name
                #Check if there is overlap in start/end time
                elif max(0, min(existing_date[2], incoming_date[2]) - max(existing_date[1], incoming_date[1])) > 0:
                    return True, appt_name
        return False, None

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
        '''
        appointment = (
            name: str, 
            day: int, 
            start_time: float, 
            end_time: float, 
            participants: list
            )
        '''
        print('\nCalendar:\n############################################################################################\n')
        if bool(self.appointments):
            col_width = max(max(len(name) for name in self.appointments.keys()), len("Appointment"))
        else:
            col_width = len("Appointment")
        week_dict = {"Sunday":[], "Monday":[], "Tuesday":[], "Wednesday":[], "Thursday":[], "Friday":[], "Saturday":[]}
        weekday_width = max(len(name) for name in week_dict.keys())
        print("{} \t {} \t {} \t {} \t {}".format("".ljust(weekday_width),"Appointment".ljust(col_width), "Start", "End", "Participants"))
        for appointmentName, appointment in self.appointments.items():
            if appointment[1] == 1:
                week_dict["Sunday"].append(list(appointment))
            elif appointment[1] == 2:
                week_dict["Monday"].append(list(appointment))
            elif appointment[1] == 3:
                week_dict["Tuesday"].append(list(appointment))
            elif appointment[1] == 4:
                week_dict["Wednesday"].append(list(appointment))
            elif appointment[1] == 5:
                week_dict["Thursday"].append(list(appointment))
            elif appointment[1] == 6:
                week_dict["Friday"].append(list(appointment))
            elif appointment[1] == 7:
                week_dict["Saturday"].append(list(appointment))
        for weekday, appt_list in week_dict.items():
            print("{}:\n------------\n".format(weekday.ljust(weekday_width)))
            if appt_list != []:
                np.argsort(np.array(appt_list)[:,2])
                for appt in appt_list:
                    print("{} \t {} \t {} \t {} \t {}".format("".ljust(weekday_width),appt[0].ljust(col_width), '{0:02.0f}:{1:02.0f}'.format(*divmod(appt[2] * 60, 60)), '{0:02.0f}:{1:02.0f}'.format(*divmod(appt[3] * 60, 60)), appt[4]))
    
    def contains(self, appointmentName: str) -> bool:
        return (appointmentName in self.appointments)

    def getAppointment(self, appointmentName: str) -> tuple:
        return self.appointments[appointmentName]


if __name__ == '__main__':
    # Testing... Testing..... 
    cal = Calendar(1, True)
    doctorAppointment = ("Doctor Appointment", 2, 12.5, 13.5, [1,2])
    dentalAppointment = ("Dentist Appointment", 2, 14.5, 18.5, [1,2])
    cal.insertAppointment(doctorAppointment)
    cal.insertAppointment(dentalAppointment)
    cal.insertAppointment(("DMV", 5, 12.5, 13.5, [4]))
    cal.insertAppointment(("Skiing", 7, 8, 18, [2,3]))
    cal.printCalendar()



