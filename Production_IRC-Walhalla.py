# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 19:47:14 2020
IRC Bot
Use cases:
    Connects to darkmyst IRC server in current implementation
    Dice Rolling
    ---
@author: Ethan 
"""

import ssl
import socket
import time
import random
import re
from datetime import datetime

HOST = "irc.darkmyst.org"
PORT = 6697

NICK = "WeaverAscendant"
IDENT = "Weaver Ascendant"
REALNAME = "Weaver Ascendant"
MASTER = "Seraphim"


#Set up the server connection using encrypted SSL
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
s = ssl_context.wrap_socket(socket.socket(), server_hostname=HOST)
s.connect((HOST, PORT))

#Send information to the IRC server to properly register and identify, without being kicked for flood
s.send(bytes("USER %s %s Walhalla :%s\r\n" % (IDENT, HOST, REALNAME), "UTF-8"))
time.sleep(1)
s.send(bytes("NICK %s\r\n" % NICK, "UTF-8"))
time.sleep(1)
s.send(bytes("JOIN #Walhalla:Dice \r\n", "UTF-8"))

             
def sendMessage(origin, message1, message2, message3):
    try:
        s.send(bytes("PRIVMSG " + origin + " :" + message1 + "\r\n", "UTF-8"))
        if message2 != '':
            s.send(bytes("PRIVMSG " + origin + " :" + message2 + "\r\n", "UTF-8"))
        if message3 != '':
            s.send(bytes("PRIVMSG " + origin + " :" + message3 + "\r\n", "UTF-8"))
    except Exception as e:
        print("sendMessage Exception: " + str(e))
        return
    return


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

def WoD(line):
    try:
        #Make index 3 lowercase, check if it is equal to !wod
        line[3] = line[3].lower()
        if "!wod" in line[3]:
            #Extract the sender of the message
            sender = line[0] #First extract index 0 of the list
            sender = sender[1:sender.find("!")] #Then extract from index 1 until the first ! from the string
            origin = line[2] #Extract channel
            print("Sender: " + origin)

            #Get variables
            willpower, numDice, difficulty, reason = getDiceFields(line)

            #Check if the user is a dick or stupid
            if int(numDice) > 50:
                message = "Please roll less than 50 dice at a time."
                sendMessage(origin, message, '', '')
                return
            elif int(numDice) < 1:
                message = "Must roll at least one die."
                sendMessage(origin, message, '', '')
                return
            if int(difficulty) < 2 or int(difficulty) > 10:
                message = "Difficulty must be in range 2-10."
                sendMessage(origin, message, '', '')
                return

            total, botch, successes, ten, diceList = WoDDice(numDice, difficulty, willpower)

            #Typecast and remove brackets
            diceList = str(diceList)
            diceList = diceList[1:-1]
            
            #message1 = "\x02\x0351@%s\x03\x02 rolled %s at difficulty %s | \u3010%s\u3011" % (sender, numDice, difficulty, str(diceList))
            #message2 = "Successes: %s, Botches: %s, \x02\x1FTotal: %s\x0F | Add %s with specialty." % (total, botch, successes, ten)
            #message3 = "%s" % (reason)
            #Just in case some site thinks pyflakes is a good thing. Backup code
            
            #Create messages to send dice output with formatting and unicode
            message1 = f"\x02\x0361@{sender}\x03\x02 rolled {numDice} at difficulty {difficulty} | \u3010{diceList}\u3011"
            message2 = f"Successes: {total}, Botches: {botch}, \x02\x1FTotal: {successes}\x0F | Add {ten} with specialty."
            message3 = f"{reason}"
            if total == 0 and botch > 0:
                message2 = f"Successes: {total}, Botches: {botch}, \x02\x1FTotal: {successes}\x0F | True Botch! -{botch}!"

            sendMessage(origin, message1, message2, message3)
            return
    #Don't allow an error to cause the entire program to fail, print nothing and return instead
    except Exception as e:
        print("WoD Exception: " + str(e))
        return

def dSidedDice(line):
    try:
        sender = line[0] #First extract index 0 of the list
        sender = sender[1:sender.find("!")] #Then extract from index 1 until the first ! from the string
        origin = line[2] #Extract channel
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
                sendMessage(origin, "Please roll less than 50 dice at a time.", '', '')
                return
            diceList, total = rollDice(numDice, dSides)
            send = 1
            
        if(send == 1):
            diceList = str(diceList)
            diceList = diceList[1:-1]
            message1 = f"\x02\x0361@{sender}\x03\x02 rolled {line[4]}: \u3010{diceList}\u3011"
            message2 = f"Total: {total}"
            
            sendMessage(origin, message1, message2, '')
    except Exception as e:
       print("dSidedDice Exception: " + e)
       return
    return

def init(line):
    try:
        sender = line[0] #First extract index 0 of the list
        sender = sender[1:sender.find("!")] #Then extract from index 1 until the first ! from the string
        origin = line[2] #Extract channel
        try:
            if re.compile("^[0-9]*$").match(line[4]) and re.compile("^[0-9]*$").match(line[5]):
                initRoll = random.randint(1,10)
                initTotal = initRoll + int(line[4]) + int(line[5])
                message1 = f"\x02\x0361@{sender}\x03\x02 rolled 1d10: {initRoll}"
                message2 = f"Initiative: {initRoll} + (Dex) {line[4]} + (Wits) {line[5]} = \x02\x1F{initTotal}\x0F"
                sendMessage(origin, message1, message2, '')
                return
        except IndexError:
            pass
        try:
            if re.compile("^[0-9]*$").match(line[4]):
                initRoll = random.randint(1,10)
                initTotal = initRoll + int(line[4])
                message1 = f"\x02\x0361@{sender}\x03\x02 rolled 1d10: {initRoll}"
                message2 = f"Initiative:  {initRoll} + (Modifier) {line[4]} = \x02\x1F{initTotal}\x0F"
                sendMessage(origin, message1, message2, '')
                return
        except IndexError:
            pass
    except Exception as e:
        print("Init Exception: " + str(e))
        return
    return


def main():
    readbuffer = ""
    s.settimeout(200)
    try:
        while 1:
            #Read input from darkmyst and add it to a list
            readbuffer = readbuffer+s.recv(2048).decode("UTF-8")
            temp = str.split(readbuffer, "\n") #Split apart by the null terminator
            readbuffer = temp.pop() #Pop off each message sent from the list created
    
            #Do the following for every line sent
            for line in temp:
    
                #If we see 376 in a line, this means the server has been joined successfully. 
                if "376" in line:
                    #Therefore we can now join a room
                    s.send(bytes("JOIN #Walhalla:Dice \r\n", "UTF-8"))
                    s.send(bytes("JOIN #FOI.Dice \r\n", "UTF-8"))
                    #s.send(bytes("PRIVMSG #BotTestRoom :I like pancakes\r\n", "UTF-8"))
                print(str(datetime.now())[11:17] + line)
                #Strip unncecessary space, and split apart into a list with each index containing a string delimited by spaces
                line = str.rstrip(line)
                line = str.split(line)
    
                #Listen for and respond for server pings. Send appropriate line back
                if line[0] == "PING":
                    s.send(bytes("PONG %s\r\n" % line[1], "UTF-8"))
                
                WoD(line)
                try:
                    if re.compile("^:!roll").match(line[3]) and re.compile("^[1-9]*[dD][1-9][0-9]*").match(line[4]):
                        dSidedDice(line)
                    if "!init" in line[3]:   
                        init(line)
                except IndexError:
                    pass
                
    except socket.timeout as e:
        print(e)
        print("Ping: irc.darkmyst.org")
        s.send(bytes("PING: irc.darkmyst.org"))

main()