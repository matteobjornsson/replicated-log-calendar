import csv
import EventRecord

class Log:

    log = []
    logFile = None
    header = ["TIME","NODE ID", "OPERATION", "APPOINTMENT NAME", "DAY", "START", "END", "PARTICIPANTS"]

    def __init__(self):
        with open('../files/logOutput.tsv', 'wt') as out_file:
            logWriter = csv.writer(out_file, delimiter='\t')
            logWriter.writerow(self.header)

    def insert(self, eR: EventRecord):
        self.log.append(eR)
        with open('../files/logOutput.tsv', 'a') as out_file:
            logWriter = csv.writer(out_file, delimiter='\t')
            logWriter.writerow(eR.iterable)

    # def hasrec(self, eR: eventRecord):

    # def truncateLog(self, eventName: str):



if __name__ == '__main__':
    log = Log()
    event = ("Doctor Appt", 3, 10.0, 11.5, [1,2])
    eR = EventRecord.EventRecord("Insert", event, 4, 1)
    log.insert(eR)

