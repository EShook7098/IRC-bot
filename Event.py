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
        
        dateFix = str.split(date, "/")
        month = dateFix[0]
        day = dateFix[1]
        if(month[0] == "0"):
            month = month[1]
        if(day[0] == "0"):
            day = day[1]
        date = month + '/' + day
        
        self.key = name
        self.date = date
        self.time = time
        self.name = name
        self.type = type
        self.link = link
        self.dateTime = date + " " + time #For later sorting
        
    
    def setEventdate(self, date):
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
  
#End Event Object definition
  
def setOrigin(origin):
    origin = origin[1:].lower()
    if origin in ("walhalla:st", "walhalla:ooc"):
        return "walhalla"
    elif origin in ("foi.st", "fate.of.illusions"):
        return "fate"
    elif origin in ("sanctum:overlords", "sanctum-ooc"):
        return "sanctum"
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
    
    if(len(inputParse[0]) > 5):
        return False, "Invalid date format. Please enter as m/d, m/dd,or as mm/dd."
    event = Event(inputParse[0],inputParse[1],inputParse[2],inputParse[3],inputParse[4])
    storeData(origin, event)
    return True, ""
            
def storeData(origin, event):
    #We need to serialize the object and still be able to access the attributes when read back
    #Therefore, we are using pickle/shelve to serialize on store and deserialize on read 
    eventFile = shelve.open(origin, "c") 
    print("Origin: " + origin)
    print("Event Key: " + event.key)
    print("Event: " + str(event))
    print(eventFile)
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
        eventData = shelve.open(origin, "w")
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
        origin = setOrigin(origin)
        eventData = shelve.open(origin, "r")
        
        myKeys = list(eventData.keys()) #Sticky issue here
        print(myKeys)
        displayList = []
        eventLength = 0
        
        currentMonth = str(datetime.now())[5:7]
        for key in myKeys:
            
            #--Handle automatic deletion on event expiration--------------------
            expirationObject = ""        
            currentTime = datetime.now()
            try:
                #print("Check: " + str(yearCheck) + " versus Event Date: " + str(eventData[key].dateTime.rsplit('/', 1)[0])) #Shows we have an issue with 09 versus 9
                #if (yearCheck[0] == "0"):
                 #   yearCheck = yearCheck[1]
                #if (ye) == True:
                #    year = str(currentTime.year)
                #else: 
                  #  year = str(currentTime.year + 1)
                if (int(currentMonth) == 12): #If not december
                    year = str(currentTime.year + 1) #This needs to change to be handled in the CREATE EVENT
                else:
                    year = str(currentTime.year)
                 
                expirationObject = datetime.strptime(eventData[key].dateTime + " " + year, "%m/%d %I:%M %p %Y")
            except ValueError:
                try:
                    expirationObject = datetime.strptime(eventData[key].dateTime + " " + year, "%m/%d %I:%M%p %Y")
                except:
                    print("Date Setting Excepted.")
                    continue
                    
                
            expirationTime = dt.datetime(expirationObject.year, expirationObject.month, expirationObject.day, expirationObject.hour, expirationObject.minute, 00, 000000)
            print("Expiration time: " + str(expirationTime))
            print("Current time: " + str(currentTime))
            if expirationTime < currentTime:
                print(key + " deleted")
                del eventData[key]
                continue
           
            #--Handle rest of the loading proceedure if an event or two are not deleted-----
            print(key)
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