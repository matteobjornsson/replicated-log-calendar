import csv
import EventRecord

class Log:
    """
    This is a class for creating Event Records objects for a replicated log 

    Attributes:
        log (list):     Container for event records in memory (vs in the log file)
        logFile (File): Reference to log file on disk
        header (list):  List containing log headers as strings
    """

    log = []
    logFile = None # to implement later, reference to log location? 
    header = ["TIME","NODE ID", "OPERATION", "APPOINTMENT NAME", "DAY", "START",
             "END", "PARTICIPANTS"]

    def __init__(self):
        """
        Constructor for Log class. 
        
        Constructor initializes (*overwriting current file!*) an empty .tsv file
        for the log with the header as the first line. 

        TODO: Constructor needs to check file location for existing log. If one
        exists it needs to populate self.log with the existing records from file
        """
        with open('../files/logOutput.tsv', 'w') as out_file:
            # this method creates a new tsv file, overwriting existing
            logWriter = csv.writer(out_file, delimiter='\t')
            logWriter.writerow(self.header)

    def insert(self, eR: EventRecord):
        self.log.append(eR)
        with open('../files/logOutput.tsv', 'a') as out_file:
            logWriter = csv.writer(out_file, delimiter='\t')
            logWriter.writerow(eR.iterable)

    def hasrec(self, eR: EventRecord):
        print("this is the hasrec function")

    def truncateLog(self, listOfEventRecords: list):
        # if all nodes know of an eventRecord, delete it from the local log
        # do that ^
        print("this is the truncate function")



if __name__ == '__main__':
    log = Log()
    event = ("Doctor Appt", 3, 10.0, 11.5, [1,2])
    eR = EventRecord.EventRecord("Insert", event, 4, 1)
    log.insert(eR)

