# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 09:38:40 2020

@author: Ethan
"""

import re
import Event
import Dice
import time

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
        self.join("Bottestroom")
        #self.join("#SD:Dice")
        #self.join("#FOI.Dice")
        #self.join("#Sanctum-Dice")
        self.join("#FOI.ST")
        self.join("#Fate.Of.Illusions")
        #self.join("#Sanctum-ooc")
        #self.join("#Sanctum-Overlords")
        #self.join("#IS.Dice")
        #self.join("#Walhalla:Dice")
        self.join("#Walhalla:ST")
        self.join("#Walhalla:OOC")
        
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
                        diceCallString = line[3].lower()
                        
                        #----------------Dice Calls----------------------------------
                        
                        if re.compile("^:!wod").match(diceCallString):
                            print("WoD!")
                            sender, origin = getSenderLocation(line)
                            message1, message2, message3 = Dice.WoD(sender, line)
                            self.sendMessages(sender, origin, message1, message2, message3, "")
                        
                        
                        elif re.compile("^:!roll").match(diceCallString) and re.compile("^[1-9]*[dD][1-9][0-9]*").match(line[4]):
                            print("Roll!")
                            sender, origin = getSenderLocation(line)
                            message1, message2, message3 = Dice.dSidedDice(sender, line)
                            self.sendMessages(sender, origin, message1, message2, message3, "")
                        
                        
                        elif "!init" in diceCallString:
                            print("Init!")
                            sender, origin = getSenderLocation(line)
                            message1, message2, message3 = Dice.init(sender, line)
                            self.sendMessages(sender, origin, message1, message2, message3, "")
                        
                       #----------------Event calls-------------------------------------
                        
                        elif re.compile("^:!setevent$").match(diceCallString):
                            sender, origin = getSenderLocation(line)
                            line = ' '.join(line)
                            line = re.sub(".*:!setevent", '', line)
                            if re.compile("^.*\|.*\|.*\|.*\|.*$").match(line):
                                print("Event set!")
                                send, errorMessage = Event.createEvent(origin, line)
                                if send == True:
                                    self.sendMessages(sender, origin, "Event created!", "", "", "")
                                else:
                                    self.sendMessages(sender, origin, errorMessage, "", "", "")
                                #Call eventList to channel/PM displayEventList()
                        
                        
                        elif ":!events" in diceCallString:
                            print("Events!")
                            sender, origin = getSenderLocation(line)
                            origin = origin.lower()
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
                       
                        
                        elif (":!walhalla" in diceCallString) or (":!sanctum" in diceCallString) or (":!foi" in diceCallString) or (":!bottestroom" in diceCallString):
                            sender, origin = getSenderLocation(line)
                            
                            command = diceCallString
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
                            
                        elif ":!delete" in diceCallString:
                            sender, origin = getSenderLocation(line)
                            key = line[4:]
                            key = ' '.join(key)
                            #print(key)
                            channels = ["#bottestroom", "#walhalla:st", "#sanctum-overlords", "#foi.st"]
                            for match in channels:
                                if match == origin.lower():
                                    eventFound = Event.deleteData(origin, key)
                            if eventFound == True:
                                message = f"{key} deleted!"
                            else:
                                message = "No event found."
                            self.sendMessages(sender, origin, message, "", "", "")
                            
                        elif re.compile("^:!set([a-z]|[A-Z])[a-z]*[A-Z]*").match(diceCallString):
                            sender, origin = getSenderLocation(line)
                            
                            editType = diceCallString
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
                        # + str(e)
                        #traceback.print_tb(e.__traceback__)
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
    def __init__(self):
        #self.channel = "#Walhalla:ST"
        #self.channel2 = "#Walhalla:Dice"
        #self.channel3 = "#Walhalla:ooc"
        self.channel4 = "#SD:Dice"
        self.channel5 = "#FOI.Dice"
        self.channel6 = "#Sanctum-Dice"
        self.channel7 = "#FOI.ST"
        self.channel8 = "#Fate.Of.Illusions"
        self.channel9 = "#Sanctum-ooc"
        self.channel10 = "#Sanctum-Overlords"
        self.channel11 = "#IS.Dice"
        self.channel12 = "#Walhalla:Dice"
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
     
    f = WeaverAscendantFactory()
    
    reactor.connectTCP("irc.darkmyst.org", 6667, f)

    reactor.run()
    #bullshit