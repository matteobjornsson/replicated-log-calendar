#import internal classes
import Calendar
import Log
import EventRecord as ER
import Messenger
#Import external libraries
import pickle, argparse, threading, numpy
from time import sleep

class Node:
	"""
	The main node logic were everything is executed.
	Each Node has access to its own Log and Calendar, 
	as well as a Messenger which is in charge of communicating 
	with the other nodes.

	Methods: 
		clock()
		receive()
			uses: update_log() and update_timetable()
		send()
		notify_of_conflict_resolution()
		check_for_incoming_messages()
		hasRec()
	User interaction methods:
		displayCalendar()
		addCalendarAppointment()
		deleteCalendarAppointment()
	"""

	received_notifications = []
	refresh_calendar = False

	def __init__(self, N: int, i: int, local = 0):
		"""
		Node constructor.
		Attributes: 
			lamportTime: keeps track of local events using a Lamport timestamp
			timeTable: the node's personal 2 dimensional timetable that keeps track 
				of timestamp knowledge across all nodes as messages are received
			nodeID: personal node ID (i.e. 1,2,3, or 4)
			log: The partial log of the node, keeping track of eventRecords.
				 An eventRecord consists of an operation (Insert/Delete), the corresponding Appointment,
				 a lamport timestamp, and the originating node.
				 This is updated/truncated as messages come in from other nodes
			calendar: The actual calendar with up-to-date appointments.
				 Each appointment consists of (Name, Day, StartTime, EndTime, Participants)
			messenger: object that enables message sending to other nodes as a calendar is updated,
				 a message includes the partial log, the timetable, and the nodeID
			
		"""
		self.lamportTime = 0
		self.timeTable = numpy.zeros((N,N))
		self.nodeID = i
		self.log = Log.Log(self.nodeID) 
		self.calendar = Calendar.Calendar(self.nodeID) 
		self.messenger = Messenger.Messenger(i, local)

		# listen for incoming messages on messege queue, pop and recieve
		receive_msg_thread = threading.Thread(
			target=self.check_for_incoming_messages
			)
		receive_msg_thread.start()

	def clock(self) -> int:
		"""
		Clock function that increases lamportTime by 1 when called
		"""
		self.lamportTime += 1
		return self.lamportTime

	## message proccessing: 

	def receive(self, received_NP_log, received_timetable, received_nodeID):
		"""
		process incoming messages. Update the timeTable and calendar accordingly. 
		options:  insert appointment
				  delete appointment
		Parameters:
			received_NP_log: partial log received from originating node
			received_timetable: timetable received from originating node
			received_nodeID: which node is the message coming from
		"""

		new_events = []
		#Iterate over incoming log
		for eventRecordFromNP in received_NP_log:
			#Create list of new eventrecords to update log later
			# (if time of incoming event time is newer (greater than) our 
			# TimeTable record of that node time append record to our log)
			if not self.hasRec(eventRecordFromNP, self.nodeID) and eventRecordFromNP not in self.log.log:  #Create list of new eventrecords to update log later
				new_events.append(eventRecordFromNP)
				print("recorded as new event: ", eventRecordFromNP.stringRepresentation)
				if eventRecordFromNP.operation == "Insert": #Update calendar object when inserting
					"""
					Check for conflicts
					"""
					try:
						self.calendar.insertAppointment(eventRecordFromNP.appointment, override=False) #Check for conflict resolution
					except ValueError:
						print("Conflict resolution triggered.")
						conflicting_eR_nodeID = -1
						#"Override = True" indicates that conflictresolution was triggered, and appt should be inserted					
						self.calendar.insertAppointment(eventRecordFromNP.appointment, override = True) 
						conflicting_appt_name = self.calendar.get_conflicting_appt_name(eventRecordFromNP.appointment) #Determine which appt is causing the conflict
						conflicting_eR = self.log.get_insert_eventrecord(conflicting_appt_name) #Retreive corresponding eventrecord based on conflicting appt
						if conflicting_eR.operation == "": #If no eventrecord for this appt was found, somethin weird happened
							print("")
						else:
							conflicting_eR_nodeID = conflicting_eR.nodeID
						#Tiebreaker based on node id's, higher node id wins the right to insert. New event is being inserted.
						if eventRecordFromNP.nodeID > conflicting_eR_nodeID:
							#Incoming event wins, existing event is "ignored", i.e. a delete has to be sent.
							print("Incoming conflicting appt takes precedence, overrides local conflict.")
							self.deleteCalendarAppointment(conflicting_appt_name)
							self.notify_of_conflict_resolution(conflicting_eR)
						elif conflicting_eR_nodeID > eventRecordFromNP.nodeID: 
							#Existing event wins, incoming event needs to be deleted.
							self.deleteCalendarAppointment(eventRecordFromNP.appointment[0])
							self.notify_of_conflict_resolution(eventRecordFromNP)
							print("Appointment was not inserted because there is a conflict. Incoming event {} is being deleted.".format(eventRecordFromNP.appointment[0]))

				elif eventRecordFromNP.operation == "Delete": #Update calendar object when deleting             
					if not self.log.check_delete_eR(eventRecordFromNP.appointment[0]): #Check if delete event was already recorded
						self.calendar.deleteAppointment(eventRecordFromNP.appointment[0])
					else:
						print("EventRecord already exists, i.e., appt was already deleted")
				self.refresh_calendar = True

		#Update timetable
		self.update_timetable(received_timetable, received_nodeID)
		
		#Write new log to file
		self.update_log(new_events)

	def update_log(self, new_events):
		"""
		Only keep relevant events based on timetable entrances 
		and write the collected relevant events to file.
		Effectively, this is the truncate log event.
		"""
		new_events.extend(self.log.log)
		updated_log = []
		for er in new_events:
			for j in range(len(self.timeTable[0])):
				if not self.hasRec(er, j+1):
					updated_log.append(er)
					break
		self.log.truncateLog(updated_log)

	def update_timetable(self, received_timetable, received_nodeID):
		"""
		Update own timetable based on incoming timetable, using Wuu and Bernstein algorithm
		"""
		for i in range(len(self.timeTable[0])): #Check timestamps in own row (if this is node 2, iterate over row 2) and compare to incoming node row
			self.timeTable[self.nodeID-1][i] = max(self.timeTable[self.nodeID-1][i], received_timetable[received_nodeID-1][i])
		
		for i in range(len(self.timeTable[0])): #Check all timetable values
			for j in range(len(self.timeTable[0])):
				self.timeTable[i][j] = max(self.timeTable[i][j], received_timetable[i][j])
		

	def send(self, to_nodeId):
		"""
		Build the partial log to be sent.
		Create message:
			(messenger event: int, partial log: [eventRecords], timetable: [[]], nodeID:int)
			Where, messenger event: 0 = log update, 1 = notification, 2 = refresh calendar
		Send a message to other nodes when a change is made to the log.
		"""
		NP = [eR for eR in self.log.log if not self.hasRec(eR, to_nodeId)]
		message = (0, NP, self.timeTable, self.nodeID)
		self.messenger.send(to_nodeId, message)
	
	def notify_of_conflict_resolution(self, deleted_event: ER):
		"""
		Send a notification to relevant nodes when conflict resolution occurs.
		"""
		appointment = deleted_event.appointment
		appt_name = appointment[0]
		participants = appointment[4]
		appt_string = "Appointment: {} \nDay: {}\nTime: from {} to {}\n".format(
			appt_name, appointment[1], appointment[2], appointment[3]
			)
		announcement = (
		    "\n***********************************************\n"
			+ "Notice:\n\n"
			+ "Due to conflicting appointments, the following\n"
			+ "appointment in which you were listed as a \n"
			+ "participant has been cancelled: \n\n"
			+ appt_string
			+ "\n***********************************************\n"

		)
		message = (1, announcement)

		for node in participants:
			if node == self.nodeID:
				self.messenger.message_queue.append(message)
			else:
				self.messenger.send(node, message)


	def check_for_incoming_messages(self):
		'''
		listen for incoming messages on messege queue, pop and recieve
		'''
		while True:
			if not self.messenger.message_queue == []:
				message = self.messenger.message_queue.pop(0)
				if message[0]== 0:
					self.receive(message[1], message[2], message[3])
				elif message[0] == 1:
					if not message[1] in self.received_notifications:
						self.received_notifications.append(message[1])
						print(message[1])
				elif message[0] == 2:
					self.refresh_calendar = True
	
	def hasRec(self, eR, otherNodeId: int):
		"""
		hasRecord function as presented in Wuu and Bernstein.
		Used to create partial log and check for new events on incoming message.
		"""
		if self.timeTable[otherNodeId-1][eR.nodeID-1] >= eR.lamportTime:
			return True
		else:
			return False
	
	"""
	User interaction logic
	"""

	def displayCalendar(self): 
		"""
		Call calendar object to print
		"""
		self.calendar.printCalendar()

	def addCalendarAppointment(self, appointment = None):
		if appointment == None:
			"""
			User input logic to add appointment with exception handling for input, 
			not the cleanest way of handling this...
			"""
			name = input("Enter the name of the appointment: ")
			while True:
				try:	
					day = int(input("Enter the day of the appointment: \n \
								Sunday: 1 \n \
								Monday: 2 \n \
								Tuesday: 3 \n \
								Wednesday: 4 \n \
								Thursday: 5 \n \
								Friday: 6 \n \
								Saturday: 7 \n"))
				except ValueError:
					print("Day needs to be entered as a number between 1-7.")
					continue
				if day > 7 or day < 1:
					print("Day cannot be less than 1 or more than 7. Please try again.")
					continue
				else:
					break
			while True:
				try:
					start_time = float(input("Enter the start time of the appointment. \n" +\
						"Use 24hr time, falling on the hour or half hour " +\
						"(e.g 8:00AM -> 8.0, 5:30pm -> 17.5): "))
				except ValueError:
					print("Start time needs to be entered as a number.")
					continue
				else:
					break
			while True:
				try:	
					end_time = float(input("Enter the end time of the appointment :"))
				except ValueError:
					print("End time needs to be entered as a number.")
					continue
				if end_time <= start_time:
					print("End time cannot be before start time.")
					continue
				else:
					break
			while True:
				try:
					participants = input("Enter the ID numbers of all participants, \
							separated by commas (e.g. 1, 3, 4): \n\n")
					part_list = [int(p.strip(' ')) for p in participants.strip('][').split(',')]
				except ValueError:
					print("List of participants must be entered as numbers separated by commas.")
					continue
				else:
					break
			"""
			If there are no problems with any input, create the appointment!
			"""
			appointment = (name, int(day), float(start_time), float(end_time), part_list)
		try:
			self.calendar.insertAppointment(appointment)
			lamportTime = self.clock()
			self.timeTable[self.nodeID-1][self.nodeID-1] = lamportTime
			eR = ER.EventRecord("Insert", appointment, lamportTime, self.nodeID)
			self.log.insert(eR)
		except ValueError:
			print("There already exists an appointment at that time for one or more of the participants. \n The appointment cannot be created.")		
		
		# send this update to all other nodes
		sleep(3) #allow time for testing purposes
		for n in self.messenger.otherNodes:
			self.send(n)


	def deleteCalendarAppointment(self, appointmentName = None):
		"""
		User input logic for deleting an appointment.
		"""
		if appointmentName == None:
			appointmentName = input(
				"Enter the exact text of the appointment name you wish to delete: "
				)
		if self.calendar.contains(appointmentName):
			print("calendar contains appointment to be deleted")
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

		# send this update to all other nodes
		for n in self.messenger.otherNodes:
			self.send(n)

	"""
	These methods are the same as above but built to take the information 
	directly as parameters.
	Used for testing
	"""

	def testAddCalendarAppointment(self, appointment: tuple) -> None:
		self.calendar.insertAppointment(appointment)

	def testDeleteCalendarAppointment(self, appointmentName: str) -> None:
		self.calendar.deleteAppointment(appointmentName)


if __name__ == '__main__':
	"""
	Testing functionality
	"""
	parser =  argparse.ArgumentParser(description='Node instance')
	parser.add_argument('nodeID', help='NodeID.', type=int)
	parser.add_argument('local', help='local or not', type=int)
	parser.add_argument('freshBoot', help='True = start fresh, False = read from file', type=bool)
	args = parser.parse_args()

	node = Node(4, args.nodeID, args.local)

	node.addCalendarAppointment()

	choices = {}
	choices[1] = ("Doctor Appointment", 2, 12.5, 13.5, [1,2])
	choices[2] = ("DMV", 3, 12.5, 13.5, [1,2,3])
	choices[3] = ("Skiing", 3, 6.0, 17.0, [3])
	choices[4] = ("Other", 7, 1.0, 3.0, [1])
	choices[5] = ("Dogwalking", 1, 3.0, 20.0, [1,2,3,4])
	choices[6] = ("Studying", 5, 22.0, 23.0, [3] )
	choices[7] = ("Church", 6, 10.0, 12.5, [2,4])

	while True:
		userChoice = input("Pick and appointment, 1-7")
		if int(userChoice)==0:
			node.deleteCalendarAppointment()
		else:
			node.addCalendarAppointment(choices[int(userChoice)])

		node.displayCalendar()

