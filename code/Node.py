import Calendar
import Log
#import PartialLog
import EventRecord as ER
import numpy
import Messenger
import pickle
import argparse
import threading
from time import sleep

class Node:

	received_notifications = []

## constructor: 

	def __init__(self, N: int, i: int, local = 0):
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

	## clock:
	def clock(self) -> int:
		self.lamportTime += 1
		return self.lamportTime

	## message proccessing: 

	def receive(self, received_NP_log, received_timetable, received_nodeID):
		"""
		process incoming messages. Update the timeTable and calendar accordingly. 
		options:  add appointment
					delete appointment
		add any appointments to the log by passing an eventRecord object to 
		addEventToLog()
		"""

		new_events = []
		print("\n Log at beginning of receive: ")
		self.log.printLog()
		for eventRecordFromNP in received_NP_log:
			print("incoming event: ", eventRecordFromNP.stringRepresentation)
			#Create list of new eventrecords to update log later
			# (if time of incoming event time is newer (greater than) our 
			# TimeTable record of that node time append record to our log)
			if not self.hasRec(eventRecordFromNP, self.nodeID) and eventRecordFromNP not in self.log.log:  #Create list of new eventrecords to update log later
				new_events.append(eventRecordFromNP)

				print("recorded as new event: ", eventRecordFromNP.stringRepresentation)
				if eventRecordFromNP.operation == "Insert": #Update calendar object when inserting
					print("incoming event operation %s for appt %s from node %d"%(eventRecordFromNP.operation, eventRecordFromNP.appointment[0], eventRecordFromNP.nodeID) )
					"""
					Check for conflicts
					"""
					try:
						self.calendar.insertAppointment(eventRecordFromNP.appointment, override=False) #Check for conflict resolution
					except ValueError:
						print("conflict resolution triggered")
						
						self.calendar.insertAppointment(eventRecordFromNP.appointment, override = True)
						conflicting_appt_name = self.calendar.get_conflicting_appt_name(eventRecordFromNP.appointment) #Currently overriding calendar appt
						conflicting_eR = self.log.get_insert_eventrecord(conflicting_appt_name)
						if conflicting_eR.operation == "": #if conflicting_eR == None:
							print("")
						else:
							conflicting_eR_nodeID = conflicting_eR.nodeID
						#Tiebreaker based on node id's, higher node id wins the insert right. New event is being inserted.
						if eventRecordFromNP.nodeID > conflicting_eR_nodeID:
							#Existing event wins, incoming event is "ignored", i.e. a delete has to be sent.
							print("Incoming conflicting appt takes precedence, overrides local conflict")
							self.deleteCalendarAppointment(conflicting_appt_name)
							print("conflicting appointment to delete that already exists: ", type(conflicting_eR), conflicting_eR.stringRepresentation)
							self.notify_of_conflict_resolution(conflicting_eR)
						elif conflicting_eR_nodeID > eventRecordFromNP.nodeID: 
							self.deleteCalendarAppointment(eventRecordFromNP.appointment[0])
							print("conflicting appointment is the incoming record: ", type(eventRecordFromNP), eventRecordFromNP.stringRepresentation)
							self.notify_of_conflict_resolution(eventRecordFromNP)
							print("Appointment was not inserted because there is a conflict. Incoming event {} is being deleted.".format(eventRecordFromNP.appointment[0]))
							#TODO: SEND DELETE TO NODES
					#else:
					#	self.calendar.insertAppointment(eventRecordFromNP.appointment, override=True)
				elif eventRecordFromNP.operation == "Delete": #Update calendar object when deleting             
					#try:
					if not self.log.check_delete_eR(eventRecordFromNP.appointment[0]):
					#except ValueError:
						# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!INSERT SKRILLEX HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
						print("No delete event detected, go ahead and delete.")
						self.calendar.deleteAppointment(eventRecordFromNP.appointment[0])
					else:
						print("EventRecord already exists, i.e., appt was already deleted")

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
					print("appended event record to updated log: \n")
					er.printEventRecord()
					break
		self.log.truncateLog(updated_log)

	def update_timetable(self, received_timetable, received_nodeID):
		for i in range(len(self.timeTable[0])): 
			self.timeTable[self.nodeID-1][i] = max(self.timeTable[self.nodeID-1][i], received_timetable[received_nodeID-1][i])
		
		for i in range(len(self.timeTable[0])): 
			for j in range(len(self.timeTable[0])):
				self.timeTable[i][j] = max(self.timeTable[i][j], received_timetable[i][j])
		

	def send(self, to_nodeId):
		"""
		message to be sent
		"""
		NP = [eR for eR in self.log.log if not self.hasRec(eR, to_nodeId)]
		message = (True, NP, self.timeTable, self.nodeID)
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
	
	def notify_of_conflict_resolution(self, deleted_event: ER):
		appointment = deleted_event.appointment
		appt_name = appointment[0]
		participants = appointment[4]
		appt_string = "Appointment: {} \nDay: {}\nTime: from {} to {}\n".format(
			appt_name, appointment[1], appointment[2], appointment[3]
			)
		announcement = (
			  "\n************************************\n"
			+ "Notice:\n\n"
			+ "Due to conflicting appointments, the following appointment in "
			+ " which you were listed as a participant has been cancelled: \n"
			+ appt_string
			+ "************************************\n"

		)
		message = (False, announcement)

		for node in participants:
			if node == self.nodeID:
				self.messenger.message_queue.append(message)
			else:
				self.messenger.send(node, message)



#    def addEventToLog(self, eR: ER) -> void:
		# use logProcessor object to add record to text file. 

	def check_for_incoming_messages(self):
		'''
		listen for incoming messages on messege queue, pop and recieve
		'''
		while True:
			if not self.messenger.message_queue == []:
				message = self.messenger.message_queue.pop(0)
				if message[0]:
					self.receive(message[1], message[2], message[3])
				else:
					if not message[1] in self.received_notifications:
						self.received_notifications.append(message[1])
						print(message[1])

## User interaction logic: 

	def addCalendarAppointment(self, appointment = None):
		if appointment == None:
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
				
			appointment = (name, int(day), float(start_time), float(end_time), part_list)
		try:
			self.calendar.insertAppointment(appointment)
			lamportTime = self.clock()
			self.timeTable[self.nodeID-1][self.nodeID-1] = lamportTime
			eR = ER.EventRecord("Insert", appointment, lamportTime, self.nodeID)
			self.log.insert(eR)

			#print("\"{}\" added to calendar.".format(appointment[0]))
		except ValueError:
			print("There already exists an appointment at that time for one or more of the participants. \n The appointment cannot be created.")		
		
		# send this update to all other nodes
		sleep(3) #allow time for testing purposes
		for n in self.messenger.otherNodes:
			self.send(n)

		#print statements for debugging
		#print('\nUpdated time table from insert event: \n')
		#print(self.timeTable)
		#print('\n')


	def deleteCalendarAppointment(self, appointmentName = None):
		
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
	parser.add_argument('freshBoot', help='True = start fresh, False = read from file', type=bool)
	args = parser.parse_args()

	node = Node(4, args.nodeID, args.local)

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


"""
time table at end of main():

self.timeTable = 
[[0. 0. 0. 0.]
 [0. 5. 0. 0.]
 [0. 0. 0. 0.]
 [0. 0. 0. 0.]]

"""