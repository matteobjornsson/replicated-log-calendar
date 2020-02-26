import logging

logging.basicConfig(level=logging.DEBUG, filename='../files/logfile.log', format='%(message)s')

counter = 0

listOfEvents = ['insert(x)', 'delete(x)', 'insert(y)', 'insert(z)', 'insert(h)']

for event in listOfEvents:
    counter += 1
    logging.debug("{}".format(counter) + ' : ' + '{}'.format(event))


