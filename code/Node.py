import Calendar
import Log
#import PartialLog
import EventRecord as ER
import numpy
import Messenger
import pickle
import argparse
import threading

class Node:

## constructor: 

	def __init__(self, N: int, i: int, local: int, freshBoot = True):
		self.lamportTime = 0
		self.timeTable = numpy.zeros((N,N))
		self.nodeID = i
		self.log = Log.Log(self.nodeID, freshBoot) 
		self.calendar = Calendar.Calendar(self.nodeID, freshBoot) 
		self.messenger = Messenger.Messenger(i, local)

		# listen for incoming messages on messege queue, pop and recieve
		receive_msg_thread = threading.Thread(
			target=self.check_for_incoming_messages
			)
		receive_msg_thread.start()

	## clock:
	def clock(self) -> int:
		self.lamportTime += 1
		return self.lamportTime

	## message proccessing: 

	def receive(self, received_NP_log, received_timetable):
		"""
		process incoming messages. Update the timeTable and calendar accordingly. 
		options:  add appointment
					delete appointment
		add any appointments to the log by passing an eventRecord object to 
		addEventToLog()
		"""
		# TODO: who is sender for TT update?
		received_nodeID = 0
		delete_events = {}
		insert_events = {}
		for eventRecordFromNP in received_NP_log:
			if not self.hasRec(eventRecordFromNP, self.nodeID):  #Create list of new eventrecords to update log later
				self.log.insert(eventRecordFromNP) #self.log.insert(eventRecordFromNP)

			#Create list of new eventrecords to update log later
			# (if time of incoming event time is newer (greater than) our 
			# TimeTable record of that node time append record to our log)
			if eventRecordFromNP.operation == "Insert": #Update calendar object when inserting
				#if received_nodeID == 0:
				#    received_nodeID = eventRecordFromNP.nodeID
				"""
				Check for conflicts
				"""
				try:
					self.calendar.insertAppointment(eventRecordFromNP.appointment) #Check for conflict resolution
				except ValueError:
					#Tiebreaker based on node id's, higher node id wins the insert right. New event is being inserted.
					if received_nodeID > self.nodeID:   
						self.calendar.insertAppointment(eventRecordFromNP.appointment, override=True) #Currently overriding calendar appt, TODO: not doing anything with log eventrecords!
						insert_events[eventRecordFromNP.appointment[0]] = eventRecordFromNP
					#Existing event wins, incoming event is "ignored", i.e. a delete has to be sent.
					else: 
						print("Appointment was not inserted because there is a conflict. Incoming event is being deleted.")
						#SEND DELETE TO NODES
				else:
					self.calendar.insertAppointment(eventRecordFromNP.appointment, override=True)
					insert_events[eventRecordFromNP.appointment[0]] = eventRecordFromNP
			elif eventRecordFromNP.operation == "Delete": #Update calendar object when deleting             
				self.calendar.deleteAppointment(eventRecordFromNP.appointment[0])
				delete_events[eventRecordFromNP.appointment[0]] = eventRecordFromNP
				#TODO: currently cannot handle when deleting non existing event, for example, insert arrived later.

		#Update timetable
		self.update_timetable(received_timetable, received_nodeID)

		#Write new log to file
		self.update_log()

	def update_log(self):
		"""
		Only keep relevant events based on timetable entrances 
		and write the collected relevant events to file.
		Effectively, this is the truncate log event.
		"""
		updated_log = []
		for er in (self.log.log):
			for j in range(len(self.timeTable[0])):
				if not self.hasRec(er, j):
					updated_log.append(er)
#					print("at node", j)
					break
		self.log.truncateLog(updated_log)

	def update_timetable(self, received_timetable, received_nodeID):
		for i in range(len(self.timeTable[0])): 
			self.timeTable[self.nodeID-1][i] = max(self.timeTable[self.nodeID-1][i], received_timetable[received_nodeID-1][i])
			for j in range(len(self.timeTable[0])):
				self.timeTable[i][j] = max(self.timeTable[i][j], received_timetable[i][j])
		
		print(self.timeTable)

	def send(self, to_nodeId):
		"""
		message to be sent
		"""
		NP = [eR for eR in self.log.log if not self.hasRec(eR, to_nodeId)]
		message = (NP, self.timeTable)
		self.messenger.send(to_nodeId, message)
		# send a message to other nodes when a change is made to the log
		# or as required to resolve conflicts. 
		# Use logProcessor to buld a PartialLog with hasrec() to include with
		# message. 

		''' This is for testing: 
		printableNP = []
		for eR in NP:
			printableNP.append(eR.stringRepresentation)
		print([printableNP, self.timeTable])
		message = open('incoming1.pkl', 'wb')
		pickle.dump((NP, self.timeTable), message)
		message.close()
		'''

#    def addEventToLog(self, eR: EventRecord) -> void:
		# use logProcessor object to add record to text file. 

	def check_for_incoming_messages(self):
		'''
		listen for incoming messages on messege queue, pop and recieve
		'''
		while True:
			if not self.messenger.message_queue == []:
				message = self.messenger.message_queue.pop(0)
				self.receive(message[0], message[1])


## User interaction logic: 

	def addCalendarAppointment(self, appointment = None):
		if appointment == None:
			name = input("Enter the name of the appointment: ")
			day = input("Enter the day of the appointment: \n \
						Sunday: 1 \n \
						Monday: 2 \n \
						Tuesday: 3 \n \
						Wednesday: 4 \n \
						Thursday: 5 \n \
						Friday: 6 \n \
						Saturday: 7 \n")
			start_time = input("Enter the start time of the appointment. " +\
				"Use 24hr time, falling on the hour or half hour " +\
				"(e.g 8:00AM -> 8.0, 5:30pm -> 17.5): ")
			
			end_time = input("Enter the start time of the appointment :")
			participants = input("Enter the ID numbers of all participants, \
					separated by commas (e.g. 1, 3, 4): \n\n")
			
			appointment = (name, day, start_time, end_time, participants)
		
		lamportTime = self.clock()
		self.timeTable[self.nodeID-1][self.nodeID-1] = lamportTime
		eR = ER.EventRecord("Insert", appointment, lamportTime, self.nodeID)
		self.log.insert(eR)
		try:
			self.calendar.insertAppointment(appointment)
		except ValueError:
			print("There already exists an appointment at that time for one or more of the participants. \n The appointment cannot be created.")
		print("\"{}\" added to calendar.".format(appointment[0]))


	def deleteCalendarAppointment(self):
		appointmentName = input(
			"Enter the exact text of the appointment name you wish to delete: "
			)
		if self.calendar.contains(appointmentName):
			lamportTime = self.clock()
			self.timeTable[self.nodeID-1][self.nodeID-1] = lamportTime
			eR = ER.EventRecord(
				"Delete", 
				self.calendar.getAppointment(appointmentName), 
				lamportTime, 
				self.nodeID
			)
			self.log.insert(eR)
			self.calendar.deleteAppointment(appointmentName)
			print("\"{}\" appointment deleted.\n".format(appointmentName))
		else:
			print("\"{}\" not in calendar".format(appointmentName))


	def displayCalendar(self): 
		self.calendar.printCalendar()

# These methods are the same as above but built to take the information 
# directly as parameters, 

	def testAddCalendarAppointment(self, appointment: tuple) -> None:
		self.calendar.insertAppointment(appointment)

	def testDeleteCalendarAppointment(self, appointmentName: str) -> None:
		self.calendar.deleteAppointment(appointmentName)

	def hasRec(self, eR, otherNodeId: int):
		if self.timeTable[otherNodeId-1][eR.nodeID-1] >= eR.lamportTime:
			return True
		else:
			return False


if __name__ == '__main__':
	parser =  argparse.ArgumentParser(description='Node instance')
	parser.add_argument('nodeID', help='NodeID.', type=int)
	parser.add_argument('local', help='local or not', type=int)
	args = parser.parse_args()

	node = Node(4, args.nodeID, args.local, True)
	doctorAppointment = ("Doctor Appointment", 2, 12.5, 13.5, [1,2])
	dmvAppointment = ("DMV", 4, 12.5, 13.5, [1,2])
	skiingAppointment = ("Skiing", 3, 6.0, 17.0, [3])
	otherAppointment = ("Other", 7, 1.0, 3.0, [1])
	node.addCalendarAppointment(doctorAppointment)
	node.addCalendarAppointment(dmvAppointment)
	node.addCalendarAppointment(skiingAppointment)
	# node.addCalendarAppointment()
	node.displayCalendar()
	#node.deleteCalendarAppointment()
	#node.displayCalendar()
	node.addCalendarAppointment(otherAppointment)
	node.displayCalendar()
	#print(node.timeTable)


	for n in node.messenger.otherNodes:
		node.send(n)

	"""
	try:
		read_file = open('incoming2.pkl', 'rb')
		incomingMessage = pickle.load(read_file)
		read_file.close()
	except FileNotFoundError:
		print("No incoming message available to read in")
	
	incomingNPLog = incomingMessage[0]
	incomingNPTimeTable = incomingMessage[1]
	node.receive(incomingNPLog, incomingNPTimeTable)
	node.displayCalendar()
	print(node.timeTable)
	"""

	
	

"""
time table at end of main():

self.timeTable = 
[[0. 0. 0. 0.]
 [0. 5. 0. 0.]
 [0. 0. 0. 0.]
 [0. 0. 0. 0.]]

"""