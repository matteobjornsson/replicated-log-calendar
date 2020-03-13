import csv, ast, os
import EventRecord

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

    def __init__(self, log = [], logfile = ""):
        self.log = log
        self.logfile = logfile
        if not os.path.isdir('../files'):
            os.mkdir('../files')  
        file_path = '../files/logOutput.tsv'

        try:
            with open(file_path, 'r') as read_file:
                csv_reader = csv.reader(read_file, delimiter='\t')
                next(csv_reader)
                for line in csv_reader:
                    self.log.append(self.read_log_line(line))
                    #line = read_file.readline()
        except FileNotFoundError:
            with open(file_path, 'w+') as out_file:
                logWriter = csv.writer(out_file, delimiter='\t')
                logWriter.writerow(self.header)

    def insert(self, eR: EventRecord):
        self.log.append(eR)
        with open('../files/logOutput.tsv', 'a') as out_file:
            logWriter = csv.writer(out_file, delimiter='\t')
            logWriter.writerow(eR.iterable)

    def truncateLog(self, listOfEventRecords: list):
        # if all nodes know of an eventRecord, delete it from the local log
        # do that ^
        print("this is the truncate function")

    def read_log_line(self, line):
        #print(line[7])
        participants = [p for p in ast.literal_eval(line[7])]
        appointment = (line[3], line[4], line[5], line[6], participants)
        new_record = EventRecord.EventRecord(line[2], appointment, int(line[0]), int(line[1]))
        print("read in record: ", new_record.printEventRecord())
        return new_record

if __name__ == '__main__':
    log = Log()
    event = ("Doctor Appt", 3, 10.0, 11.5, [1,2])
    eR = EventRecord.EventRecord("Insert", event, 4, 1)
    log.insert(eR)

