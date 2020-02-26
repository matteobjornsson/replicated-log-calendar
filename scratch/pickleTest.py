import pickle

testDictionary = {
  1 : "CalendarEvent1",
  2 : "CalendarEvent2",
  3 : "CalendarEvent3"
}

print("dictionary object: " + str(testDictionary))

<<<<<<< HEAD
<<<<<<< HEAD
with open('../files/calendar.pickle', 'wb') as test_dictionary_file:
=======
with open('../files/test.dictionary', 'wb') as test_dictionary_file:
>>>>>>> ff1d7534178d26b8d9cbb85fb3ee35d652df681f
=======
with open('../files/test.dictionary', 'wb') as test_dictionary_file:
>>>>>>> ff1d7534178d26b8d9cbb85fb3ee35d652df681f
    pickle.dump(testDictionary, test_dictionary_file)

print("dictionary has been pickled")

<<<<<<< HEAD
<<<<<<< HEAD
testDictionary[4] = 'BonusCalendarEvent'

with open('../files/calendar.pickle', 'wb') as test_dictionary_file:
    pickle.dump(testDictionary, test_dictionary_file)

print("modified dictionary has been pickled")

with open('../files/calendar.pickle', 'rb') as test_dictionary_file:
=======
with open('../files/test.dictionary', 'rb') as test_dictionary_file:
>>>>>>> ff1d7534178d26b8d9cbb85fb3ee35d652df681f
=======
with open('../files/test.dictionary', 'rb') as test_dictionary_file:
>>>>>>> ff1d7534178d26b8d9cbb85fb3ee35d652df681f
 
    unpickledTestDictionary = pickle.load(test_dictionary_file)

print(unpickledTestDictionary)

print('dictionary has been unpickled')

