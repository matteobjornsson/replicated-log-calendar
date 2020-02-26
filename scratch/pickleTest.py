import pickle

testDictionary = {
  1 : "CalendarEvent1",
  2 : "CalendarEvent2",
  3 : "CalendarEvent3"
}

print("dictionary object: " + str(testDictionary))

with open('../files/test.dictionary', 'wb') as test_dictionary_file:
    pickle.dump(testDictionary, test_dictionary_file)

print("dictionary has been pickled")

with open('../files/test.dictionary', 'rb') as test_dictionary_file:
 
    unpickledTestDictionary = pickle.load(test_dictionary_file)

print(unpickledTestDictionary)

print('dictionary has been unpickled')

