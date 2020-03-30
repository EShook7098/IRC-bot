# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 09:38:40 2020

@author: Ethan
"""

import random
import re
import Event
import traceback
import time

#Rolls dice, a cat could read this part
def WoDDice(numDice, difficulty, willpower):
    try:
        botch = 0
        total = 0
        rolls = 0
        ten = 0
        successes = 0
        diceList = []
        
        while int(numDice) > rolls:
            rolls = rolls + 1
            check = random.randint(1, 10)
            diceList.append(check)
            
            if check >= int(difficulty):
                total = total + 1
                if check == 10:
                    ten = ten + 1
                    
            if check == 1:
                botch = botch + 1
        
        successes = total - botch
        ten = ten - botch
        if(ten < 0):
            ten = 0
            
        diceList.sort(reverse=True)
        successes = successes+int(willpower)
        return total, botch, successes, ten, diceList
    except Exception as e:
        print("WoDDice Exception: " + str(e))
        return

#Extract the information we want from each line
def getDiceFields(line):
    try:
        reason = ''
        numDice = 0
        difficulty = 0
        willpower = 0
    
        try:
            #WP will be in index 6, make it lower case and check if it matches the regex or not
            willpowerCheck = line[6].lower()
            if re.compile("^\+?wp$|^1$").match(willpowerCheck): 
                willpower = 1
                try:
                    #If the WP is in index 6, the user reason is line 7 and greater
                    reason = ' '.join(line[7:])
                    if(reason != '' and reason != ' '):
                        reason = "Reason: " + reason
                except ValueError:
                    reason = ''
                except IndexError:
                    reason = ''
            else:
                try:
                    #If WP isn't in index 6, the reason is
                    reason = ' '.join(line[6:])
                    if(reason != '' and reason != ' '):
                        reason = 'Reason: ' + reason
                        print(reason)
                except IndexError:
                    reason = ''
        except IndexError:
            willpower = 0
    
        numDice = line[4] #Extracts dice and difficulty
        difficulty = line[5]
    except Exception as e:
        print("getDiceFields Exception: " + str(e))
    return willpower, numDice, difficulty, reason

def rollDice(numDice, dSides):
    try:
        rolls = 0
        total = 0
        diceList = []
        
        while int(numDice) > rolls:
            rolls += 1
            check = random.randint(1, int(dSides))
            total += check
            diceList.append(check)
    except Exception as e:
        print("rollDice Exception: " + str(e))
        return
    return diceList, total

def setEvent():
    return

def WoD(sender, line):
    try:
        #Get variables
        willpower, numDice, difficulty, reason = getDiceFields(line)

        #Check if the user is a dick or stupid
        if int(numDice) > 50:
            message1 = "Please roll less than 50 dice at a time."
            return message1, "", ""
        elif int(numDice) < 1:
            message1 = "Must roll at least one die."
            return message1, "", ""
        if int(difficulty) < 2 or int(difficulty) > 10:
            message1 = "Difficulty must be in range 2-10."
            return message1, "", ""

        total, botch, successes, ten, diceList = WoDDice(numDice, difficulty, willpower)

        #Typecast and remove brackets
        diceList = str(diceList)
        diceList = diceList[1:-1]
        
        #message1 = "\x02\x0351@%s\x03\x02 rolled %s at difficulty %s | \u3010%s\u3011" % (sender, numDice, difficulty, str(diceList))
        #message2 = "Successes: %s, Botches: %s, \x02\x1FTotal: %s\x0F | Add %s with specialty." % (total, botch, successes, ten)
        #message3 = "%s" % (reason)
        #Just in case pyflakes decides fstring isn't real. Backup code
        
        #Create messages to send dice output with formatting and unicode
        message1 = f"\x02\x0361@{sender}\x03\x02 rolled {numDice} at difficulty {difficulty} | \u3010{diceList}\u3011"
        message2 = f"Successes: {total}, Botches: {botch}, \x02\x1FTotal: {successes}\x0F | Add {ten} with specialty."
        message3 = f"{reason}"
        if total == 0 and botch > 0:
            message2 = f"Successes: {total}, Botches: {botch}, \x02\x1FTotal: {successes}\x0F | True Botch! -{botch}!"

        #sendMessage(sender, origin, message1, message2, message3)
        return message1, message2, message3
    #Don't allow an error to cause the entire program to fail, print nothing and return instead
    except Exception as e:
        print("WoD Exception: " + str(e))
        return

def dSidedDice(sender, line):
    try:
        send = 0
        numDice = 1
        dSides = 0
        diceSplit = line[4].split("d")
        dSides = diceSplit[1]
    
        if diceSplit[0] == '':
            diceList, total = rollDice(numDice, dSides)
            send = 1
        
        elif re.compile("^[1-9]*$").match(diceSplit[0]):
            numDice = diceSplit[0]
            if int(numDice) > 50:
                message1 = "Please roll less than 50 dice at a time."
                return message1, "", ""
            diceList, total = rollDice(numDice, dSides)
            send = 1
            
        if(send == 1):
            diceList = str(diceList)
            diceList = diceList[1:-1]
            message1 = f"\x02\x0361@{sender}\x03\x02 rolled {line[4]}: \u3010{diceList}\u3011"
            message2 = f"Total: {total}"
            
            return  message1, message2, ""
    except Exception as e:
       print("dSidedDice Exception: " + e)
       return

def init(sender, line):
    try:
        try:
            if re.compile("^[0-9]*$").match(line[4]) and re.compile("^[0-9]*$").match(line[5]):
                initRoll = random.randint(1,10)
                initTotal = initRoll + int(line[4]) + int(line[5])
                message1 = f"\x02\x0361@{sender}\x03\x02 rolled 1d10: {initRoll}"
                message2 = f"Initiative: {initRoll} + (Dex) {line[4]} + (Wits) {line[5]} = \x02\x1F{initTotal}\x0F"
                return message1, message2, ""
        except IndexError:
            pass
        try:
            if re.compile("^[0-9]*$").match(line[4]):
                initRoll = random.randint(1,10)
                initTotal = initRoll + int(line[4])
                message1 = f"\x02\x0361@{sender}\x03\x02 rolled 1d10: {initRoll}"
                message2 = f"Initiative:  {initRoll} + (Modifier) {line[4]} = \x02\x1F{initTotal}\x0F"
                return message1, message2, ""
        except IndexError:
            pass
    except Exception as e:
        print("Init Exception: " + str(e))
        return


#Protocol does protocol parsing and handling.
#An instance of this class is always instantiated when a connection is made and erased when the connection ends.
#Therefore it is not persistent.
#Persistent configuration is kept in ClientFactory.
#Asynchronous data handling, responds as events arrive
#We can instantiate new subclasses of protocol that will inherit the functions of the superclass
#https://twistedmatrix.com/documents/16.1.0/api/twisted.internet.protocol.Protocol.html

#Reactor is the core of the event loop. It waits and dispatches events and handles 
#network communications and event dispatching in our program.
#https://twistedmatrix.com/documents/16.1.0/api/twisted.internet.interfaces.IReactorCore.html

#ClientFactory creates the Protocol and receives events related to the state of our connection. 
#This powerful tool allows us to reconnect in the event of a connnection error.
#And is the crux of why this bot transitioned from socket to Twisted. Reconnection.
#https://twistedmatrix.com/documents/16.1.0/api/twisted.internet.protocol.ClientFactory.html

from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.words.protocols import irc

def getSenderLocation(line):
    #Extract the sender of the message
    sender = line[0] #First extract index 0 of the list
    sender = sender[2:sender.find("!")] #Then extract from index 1 until the first ! from the string
    origin = line[2] #Extract channel
    return sender, origin
    
class WeaverAscendant(irc.IRCClient):
    
    nickname = "WeaverAscendant"
    
    def connectionMade(self): 
        irc.IRCClient.connectionMade(self)
        #self.logger = MessageLogger(open(self.factory.filename, "a"))
        #self.logger.log(f"Connected...")
        print("Connected...")

        
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        #self.logger.log("[Disconnected at {datetime.now()}]")
        #self.logger.close()
        
    def privmsg(self, user, channel, msg):
        pass
    
    def signedOn(self):
        self.join(self.factory.channel)
        self.join(self.factory.channel2)
        self.join(self.factory.channel3)
        self.join(self.factory.channel4)
        self.join(self.factory.channel5)
        self.join(self.factory.channel6)
        self.join(self.factory.channel7)
        self.join(self.factory.channel8)
        self.join(self.factory.channel9)
        self.join(self.factory.channel10)
        
    def dataReceived(self, bytes):
        readbuffer  = repr(bytes)
        readbuffer = readbuffer.replace("'", "")
        temp = str.split(readbuffer, "\\r\\n") #Split apart by the null terminator
        try:
            for x in range(len(temp)):
                if(temp[x] != ''):
                    line = str.split(temp[x])
                    print(line)
                    try:
                        line[3] = line[3].lower()
                        
                        #----------------Dice Calls----------------------------------
                        
                        if re.compile("^:!wod").match(line[3]):
                            print("WoD!")
                            sender, origin = getSenderLocation(line)
                            message1, message2, message3 = WoD(sender, line)
                            self.sendMessages(sender, origin, message1, message2, message3, "")
                        
                        
                        elif re.compile("^:!roll").match(line[3]) and re.compile("^[1-9]*[dD][1-9][0-9]*").match(line[4]):
                            print("Roll!")
                            sender, origin = getSenderLocation(line)
                            message1, message2, message3 = dSidedDice(sender, line)
                            self.sendMessages(sender, origin, message1, message2, message3, "")
                        
                        
                        elif "!init" in line[3]:
                            print("Init!")
                            sender, origin = getSenderLocation(line)
                            message1, message2, message3 = init(sender, line)
                            self.sendMessages(sender, origin, message1, message2, message3, "")
                        
                       #----------------Event calls-------------------------------------
                        
                        elif re.compile("^:!setevent$").match(line[3]):
                            print("Top")
                            sender, origin = getSenderLocation(line)
                            line = ' '.join(line)
                            line = re.sub(".*:!setevent", '', line)
                            if re.compile("^.*\|.*\|.*\|.*\|.*$").match(line):
                                print("Event set!")
                                send = Event.createEvent(origin, line)
                                if send == True:
                                    self.sendMessages(sender, origin, "Event created!", "", "", "")
                                #Call eventList to channel/PM displayEventList()
                        
                        
                        elif ":!events" in line[3]:
                            print("Events!")
                            sender, origin = getSenderLocation(line)
                            print(origin)
                            origin = origin.lower()
                            print(origin)
                            if (origin != "#walhalla:ooc") and (origin != "#sanctum.ooc") and (origin != "#fate.of.illusions") and (origin != "#bottestroom"):
                                continue
                            sortedList = Event.loadData(origin, line)
                            message1 = "Next two events: All times CST"
                            message5 = "---------------------------------------"
                            self.sendMessages(sender, origin, message1, message5, "", "")
                            for n in range(0, 2):
                                message1 = f"{sortedList[n].name}"
                                message2 = f"{sortedList[n].date} | {sortedList[n].time}"
                                message3 = f"{sortedList[n].type}"
                                message4 = f"{sortedList[n].link}"
                                self.sendMessages(sender, origin, message1, message2, message3, message4)   
                                self.sendMessages(sender, origin, message5, "", "", "") 
                            print("Retrieved")
                       
                        
                        elif (":!walhalla" in line[3]) or (":!sanctum" in line[3]) or (":!foi" in line[3]) or (":!bottestroom" in line[3]):
                            sender, origin = getSenderLocation(line)
                            
                            command = line[3]
                            command = command[2:].lower()
                            if command in origin.lower():
                                pass
                            elif ((origin == "#Fate.Of.Illusions") and (command == "foi")):
                                pass
                            else:
                                continue
                            sortedList = Event.loadData(origin, line)
                            if sortedList == []:
                                continue
                            message1 = "Events for channel: All times CST"
                            self.sendMessages(sender, origin, message1, "", "", "")
                            for n in range(0, len(sortedList)):
                                message1 = f"{sortedList[n].dateTime} | {sortedList[n].name}"
                                self.sendMessages(sender, origin, message1, "", "", "")
                            
                        elif ":!delete" in line[3]:
                            sender, origin = getSenderLocation(line)
                            key = line[4:]
                            print(key)
                            key = ' '.join(key)
                            print(key)
                            channels = ["#bottestroom", "#walhalla:st", "#sanctum-overlords", "#foi.st"]
                            for match in channels:
                                if match == origin.lower():
                                    eventFound = Event.deleteData(origin, key)
                            if eventFound == True:
                                message = f"{key} deleted!"
                            else:
                                message = "No event found."
                            self.sendMessages(sender, origin, message, "", "", "")
                            
                        elif re.compile("^:!set([a-z]|[A-Z])[a-z]*[A-Z]*").match(line[3]):
                            sender, origin = getSenderLocation(line)
                            
                            editType = line[3]
                            editType = editType[2:]
                            print(editType)
                            line = ' '.join(line)
                            print("line: " + line)
                            input = re.sub(".*:!set([a-z]|[A-Z])[a-z]*[A-Z]*", '', line)
                            input = input.split(" | ")
                            print(input)
                            
                            listPosition = 0
                            for string in input:
                                if (string[0] == " "):
                                    string = string[1:]
                                if(string[-1] == " "):
                                    string = string[:-1]
                                input[listPosition] = string
                                listPosition += 1
                                
                            key = input[0]
                            change = input[1]
                            
                            Event.editData(origin, editType, key, change)
                            
                            #--------------------------------------------------------
                            
                    except Exception as e:                     
                        print("Inner Data Exception: " + str(e))                       
                        traceback.print_tb(e.__traceback__)
                        pass
        except Exception as e:
            print("Receiving Data Exception: " + str(e))
            pass
        return irc.IRCClient.dataReceived(self,bytes)
    
    def sendMessages(self, sender, origin, message1, message2, message3, message4):
        time.sleep(0.1)
        self.msg(origin, message1)
        if(message2 != ""):
            time.sleep(0.1)
            self.msg(origin, message2)
        else:
            return #If there isn't a second message, there isn't a third. Save a microsecond and return now
        if(message3 != ""):
            time.sleep(0.1)
            self.msg(origin, message3)
        if(message4 != ""):
            time.sleep(0.1)
            self.msg(origin, message4)
        return
class WeaverAscendantFactory(ReconnectingClientFactory):
    def __init__(self, channel, channel2, channel3, channel4, channel5, channel6, channel7, channel8, channel9, channel10, filename):
        self.channel = channel
        self.channel2 = channel2
        self.channel3 = channel3
        self.channel4 = channel4
        self.channel5 = channel5
        self.channel6 = channel6
        self.channel7 = channel7
        self.channel8 = channel8
        self.channel9 = channel9
        self.channel10 = channel10
        self.filename = filename
        self.initialDelay = 180
        self.maxDelay = 190
        self.factor = 2
        self.maxRetries = 15
        
    def buildProtocol(self, addr):
        print("Connected factory...")
        protocol = WeaverAscendant()
        protocol.factory = self
        self.resetDelay()
        return protocol
    
    def startedConnecting(self, connector):
        print("Attempting connection...")   
        
    def clientConnectionLost(self, connector, reason):
        print("Connection lost: " + str(reason))
        print("Trying to reconnect: ")
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)              

    def clientConnectionFailed(self, connector, reason):
        print("Unable to connect: " + str(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

if __name__ == '__main__':
    
    readbuffer = ''
    
    f = WeaverAscendantFactory("#Walhalla:ST", "#Walhalla:ooc", "#Walhalla:dice", "#FOI.Dice", "#Sanctum-Dice", "#FOI.ST", "#Fate.Of.Illusions", "#Sanctum-ooc", "#Sanctum-Overlords", "#IS.Dice", "FileTest2.txt")
    
    reactor.connectTCP("irc.darkmyst.org", 6667, f)

    reactor.run()