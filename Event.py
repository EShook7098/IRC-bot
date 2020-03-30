# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:26:38 2020

@author: Ethan
"""
import shelve
import traceback
from datetime import datetime
import datetime as dt

class Event:
    #Thing to think on and maybe implement
    #attrs.org, marshmellow
    def __init__(self, date, time, name, type, link):
        self.key = name
        self.date = date
        self.time = time
        self.name = name
        self.type = type
        self.link = link
        self.dateTime = date + " " + time #For later sorting
        
    
    def setEventdate(self, date):
        print("Second object reference at line 24" + self)
        self.date = date
        self.dateTime = date + " " + self.time
        
    def setEventTime(self, time):
        self.time = time
        self.dateTime = self.date + " " + time
            
    def setEventName(self, name):
        self.name = name
        
    def setEventType(self, type):
        self.type = type
    
    def setEventLink(self, link):
        self.link = link
    
    def setEventDateTime(self, date, time):
        self.dateTime = date + " " + time
  
def setOrigin(origin):
    origin = origin[1:].lower()
    if origin == "walhalla:st":
        return "Walhalla:ooc"
    elif origin == "foi.st":
        return "Fate.of.illusions"
    elif origin == "sanctum-overlords":
        return "Sanctum-ooc"
    elif origin == "bottestroom":
        return "BotTestRoom"
    else:
        return False
    
def createEvent(origin, input):
    origin = setOrigin(origin)
    if origin == False:
        return False
    inputParse = input[1:]
    print(inputParse)
    inputParse = inputParse.split("|")
    
    #We want to format the string for best display properties.
    #Removing leading and trailing spaces from every attribute
    listPosition = 0
    for string in inputParse:
        if (string[0] == " "):
            string = string[1:]
        if(string[-1] == " "):
            string = string[:-1]
        inputParse[listPosition] = string   
        listPosition += 1
    
    event = Event(inputParse[0],inputParse[1],inputParse[2],inputParse[3],inputParse[4])
    storeData(origin, event)
    return True
            
def storeData(origin, event):
    #We need to serialize the object and still be able to access the attributes when read back
    #Therefore, we are using pickle/shelve to serialize on store and deserialize on read 
    eventFile = shelve.open(origin) 
    try:
        eventFile[event.key] = event
    except KeyError as e:
        "No key found: " + str(e)
    finally:
        eventFile.close()
        return

def editData(origin, editType, changeKey, change):
    try:
        editType = editType.lower()
        origin = setOrigin(origin)
        eventData = shelve.open(origin)
        
        for key, event in eventData.items():
            print(key)
            print(key.lower() + " | " + changeKey.lower())
            if(key.lower() == changeKey.lower()):
                if editType == "setdate":
                    #print("Changing...")
                    #Javascript nightmares continue here
                    #Cannot call eventData[key].setEventDate(change) to change it
                    #This seems to be an artifact of shelve, with different object ID's being referenced
                    #If an instance function is called
                    eventInfo = eventData[key]
                    eventInfo.date = change
                    eventInfo.dateTime = change + " " + eventInfo.time
                    print(eventInfo.dateTime)
                    eventData[key] = eventInfo
                    print(eventData[key])
                    
                elif editType == "settime":
                    eventInfo = eventData[key]
                    eventInfo.time = change
                    eventInfo.dateTime = eventInfo.date + " " + change
                    eventData[key] = eventInfo
                    
                elif editType == "setname":
                    eventInfo = eventData[key]
                    eventInfo.name = change
                    eventInfo.key = change
                    del eventData[key]
                    eventData[eventInfo.key] = eventInfo
                
                elif editType == "settype":
                    eventInfo = eventData[key]
                    eventInfo.type = change
                    eventData[key] = eventInfo
                    
                elif editType == "setlink":
                    eventInfo = eventData[key]
                    eventInfo.link = change
                    eventData[key] = eventInfo    
                    
        eventData.close()
    except Exception as e:
        eventData.close()
        traceback.print_tb(e.__traceback__)
        
    
def deleteData(origin, deletionKey):
    try:
        origin = setOrigin(origin)
        eventData = shelve.open(origin)
        myKeys = list(eventData.keys())
        eventFound = False
        
        for key in myKeys:
            if(key.lower() == deletionKey.lower()):
                print(key.lower() + " | " + deletionKey.lower())
                print(key + " deleted")
                del(eventData[key])
                eventFound = True
        eventData.close()
        return eventFound
    except Exception as e:
        eventData.close()
        traceback.print_tb(e.__traceback__)
        return False
    
def loadData(origin, line):
    try:
        #command = line[3]
        #command = command[2:].lower()
        #print(command)
        print(origin)
        eventData = shelve.open(origin[1:])
        print(eventData)
        #data = pickle.load(eventFile)
        myKeys = list(eventData.keys())
        print(myKeys)
        displayList = []
        eventLength = 0
        
        yearCheck = str(datetime.now())[5:7]
        print(eventData)
        for key in myKeys:
            
            #--Handle automatic deletion on event expiration--------------------
            expirationObject = ""        
            currentTime = datetime.now()
            try:
                if (int(yearCheck) <= int(eventData[key].dateTime.rsplit('/', 1)[0])) == True:
                    year = str(currentTime.year)
                else: 
                    year = str(currentTime.year + 1)
                expirationObject = datetime.strptime(eventData[key].dateTime + " " + year, "%m/%d %I:%M %p %Y")
            except ValueError:
                try:
                    expirationObject = datetime.strptime(eventData[key].dateTime + " " + year, "%m/%d %I:%M%p %Y")
                except:
                    continue
                
            expirationTime = dt.datetime(expirationObject.year, expirationObject.month, expirationObject.day, expirationObject.hour, expirationObject.minute, 00, 000000)
            
            if expirationTime < currentTime:
                print(key + " deleted")
                del eventData[key]
                continue
           
            #--Handle rest of the loading proceedure if an event or two are not deleted-----
            
            data = eventData[key]
            displayList.append(data)
            eventLength += 1
            
        sortedList = sorted(displayList, key = lambda event: event.dateTime, reverse = False)
        #for n in range(0,eventLength):
            #print(sortedList[n].name)
        eventData.close()

    except Exception as e:
        eventData.close()
        traceback.print_tb(e.__traceback__)
        return []
    
    return sortedList