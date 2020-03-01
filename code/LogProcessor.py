import logging

class LogProcessor:

    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG, 
            filename='../files/logfile.log', 
            format='%(message)s')

    # events inserted into log need to retain event information, time,
    # and node, as well as be human readable
    def appendToLog(self, msg: str) -> None:
        logging.debug(msg)

#   def truncateLog(self):
        # not sure if this method is necessary, truncating could happen
        # automatically in msg receive

#   def hasrec(self, timeTable: numpy Array, eR: EventRecord, nodeID: int ) -> Bool:
        # not sure if this method should happen here


if __name__ == '__main__':

    log = LogProcessor()

    counter = 0

    listOfEvents = ['insert(x)', 'delete(x)', 'insert(y)', 'insert(z)', 'insert(h)']

    for event in listOfEvents:
        counter += 1
        log.appendToLog("{}".format(counter) + ' : ' + '{}'.format(event))


