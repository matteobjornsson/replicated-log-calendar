import csv, ast, os
import EventRecord

class LogEventError(ValueError):
    '''Raise error when log eventrecord does not exist'''
    def __init__(self, message):
        self.message = message

"""
Log keeps track of all events that have occurred. 
There are two types of events that can happen in this program:
'insert' and 'delete' of a calendar appointment.
EventRecord to be added has the following structure:
            operation (str):        Operation, e.g. "Insert" or "Delete"
            appointment (tuple):    Calendar Appointment subject to operation
            lamportTime (int):      event order on parent node
            nodeID (int):           parent node ID 
Where Calendar tuple is structured as follows:
            appointment = (
            name: str, 
            day: int, 
            start_time: float, 
            end_time: float, 
            participants: list
            )
"""

class Log:
    header = ["TIME","NODE ID", "OPERATION", "APPOINTMENT NAME", "DAY", "START", "END", "PARTICIPANTS"]

    def __init__(self, nodeID: int):
        """
        Log constructor
        Attributes:
            log: list of eventrecords
            file_path: filepath to read and write from

        """
        self.log = []
        self.logfile = ''
        if not os.path.isdir('../files'):
            os.mkdir('../files') 
        filename = "logOutput" + str(nodeID) + ".tsv" 
        self.file_path = '../files/' + filename
        try:
            with open(self.file_path, 'r') as read_file:
                csv_reader = csv.reader(read_file, delimiter='\t')
                next(csv_reader)
                for line in csv_reader:
                    self.log.append(self.read_log_line(line))
                    #line = read_file.readline()
        except FileNotFoundError:
            with open(self.file_path, 'w+') as out_file:
                logWriter = csv.writer(out_file, delimiter='\t')
                logWriter.writerow(self.header)

    def insert(self, eR: EventRecord):
        """
        Insert new eventrecord (can be delete or insert appointment),
        and add to file
        """
        self.log.append(eR)

        with open(self.file_path, 'a') as out_file:
            logWriter = csv.writer(out_file, delimiter='\t')
            logWriter.writerow(eR.iterable)
    
    def get_insert_eventrecord(self, eR_name):
        """
        Check whether insert event already exists in log
        """
        for er in self.log:
            if er.appointment[0] == eR_name and er.operation == "Insert":
                return er

        return EventRecord.EventRecord("", ("", -1, -1, -1, []), -1, -1)
        #raise LogEventError("") #No existing eventrecord with name" + eR_name + " operation " + eR_operation) #Sadly this caused some issues...
    
    def check_delete_eR(self, eR_name):
        """
        Check whether delete event already exists in log
        """
        for er in self.log:
            if er.appointment[0] == eR_name and er.operation == "Delete":
                return True
        return False

    def truncateLog(self, eventRecords):
        """
        If all nodes know of an eventRecord, delete it from the local log 
        """
        with open(self.file_path, 'w') as out_file:
            logWriter = csv.writer(out_file, delimiter='\t')
            for eR in eventRecords:
                logWriter.writerow(eR.iterable)
        self.log = eventRecords

    def read_log_line(self, line):
        """
        Reading a single line in a log
        """
        participants = [p for p in ast.literal_eval(line[7])]
        appointment = (line[3], line[4], line[5], line[6], participants)
        new_record = EventRecord.EventRecord(line[2], appointment, int(line[0]), int(line[1]))
        print("read in record: ", new_record.printEventRecord())
        return new_record

    def printLogFromLogfile(self):
        """
        Printing entire partial log from existing file
        """
        with open(self.file_path, 'r') as read_file:
            csv_reader = csv.reader(read_file, delimiter='\t')
            next(csv_reader)
            for line in csv_reader:
                print(line)

    def printLog(self):
        """
        Printing partial log from current memory, i.e., saved python object
        """
        print("TIME\tNODEID\tOP\tNAME\tDAY\tSTART\tEND\tPARTICIPANTS")
        for x in self.log:
            print(x.stringRepresentation)


if __name__ == '__main__':
    #TESTING
    log = Log()
    event = ("Doctor Appt", 3, 10.0, 11.5, [1,2])
    eR = EventRecord.EventRecord("Insert", event, 4, 1)
    log.insert(eR)

