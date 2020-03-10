import csv, ast
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
        try:
            with open('../files/logOutput.tsv', 'r') as read_file:
                line = read_file.readline()
                while line:
                    self.log.append(self.read_log_line(line))
                    line = read_file.readline()
        except FileNotFoundError:
            with open('../files/logOutput.tsv', 'wt') as out_file:
                logWriter = csv.writer(out_file, delimiter='\t')
                logWriter.writerow(self.header)

    def insert(self, eR: EventRecord):
        self.log.append(eR)
        with open('../files/logOutput.tsv', 'a') as out_file:
            logWriter = csv.writer(out_file, delimiter='\t')
            logWriter.writerow(eR.iterable)

    # def truncateLog(self, eventName: str):

    def read_log_line(self, line):
        participants = [p.strip() for p in ast.literal_eval(line[7])]
        appointment = (line[3], line[4], line[5], line[6], participants)
        new_record = EventRecord(line[2], appointment, int(line[0]), int(line[1]))
        print("read in record: ", new_record.printEventRecord())
        return new_record

if __name__ == '__main__':
    log = Log()
    event = ("Doctor Appt", 3, 10.0, 11.5, [1,2])
    eR = EventRecord.EventRecord("Insert", event, 4, 1)
    log.insert(eR)

