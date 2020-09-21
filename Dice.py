# -*- coding: utf-8 -*-
"""
Created on Mon May 25 10:35:02 2020

@author: Ethan
This file handles all dice functions for our bot
"""
import random
import re
import traceback

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
                successes = successes + 1
                if check == 10:
                    ten = ten + 1
                    
            if check == 1:
                botch = botch + 1
        
        total = successes - botch
        ten = ten - botch
        if(ten < 0):
            ten = 0
            
        diceList.sort(reverse=True)
        total = total+int(willpower)
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
        specialty = False
    
        try:
            #WP will be in index 6, make it lower case and check if it matches the regex or not
            #willpowerCheck = line[6].lower()
            #The reason we cannot execute these as if elif is due to creating error catching and ensuring fields are set before a potential exception is thrown
            #There is likely a better way to do this, look into it for good practice
            if re.compile("^\+wp|\+w|wp").match(line[6].lower()): 
                willpower = 1
            if re.compile("^\+?sp|\+?s").match(line[6].lower()):
                specialty = True
            if re.compile("^\+?sp|\+?s").match(line[7].lower()):
                specialty = True
            if re.compile("^\+wp|\+w|wp").match(line[7].lower()):
                willpower = 1

        except IndexError as e:
            print("getDiceFields: Outer Index Error: " + str(e))

            #Here is determined where the reason message will begin from, we do not want to include extraneous data
            #Only what remains after the potential wp and sp fields are set
            try:
                if specialty == True or willpower == 1:
                    reason = ' '.join(line[7:])
                    if reason != '' and reason != ' ':
                        reason = "Reason: " + reason
                elif specialty == True and willpower == 1:
                    reason = ' '.join(line[8:])
                    if reason != '' and reason != ' ':
                        reason = "Reason: " + reason
                else:
                    reason = ' '.join(line[6:])
                    if reason != '' and reason != ' ':
                        reason = "Reason: " + reason
            except ValueError as e:
                print("Inner Value Error: ")
                reason = ''
            except IndexError as e:
                print("Inner Index Error: ")
                reason = ''
                
        numDice = line[4] #Extracts dice and difficulty
        difficulty = line[5]
    except Exception as e:
        print("getDiceFields: Exception: " + str(e))
    return willpower, numDice, difficulty, reason, specialty

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


def WoD(sender, line):
    try:
        #Get variables
        willpower, numDice, difficulty, reason, specialty = getDiceFields(line)

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
        message1 = f"\x02@{sender}\x02 rolled {numDice} at difficulty {difficulty} | \u3010{diceList}\u3011"
        message2 = f"Successes: {successes}, Botches: {botch}, \x02\x1FTotal: {total}\x0F | Add {ten} with specialty."
        message3 = f"{reason}"
        if successes == 0 and botch > 0:
            message2 = f"Successes: {successes}, Botches: {botch}, \x02\x1FTotal: {total}\x0F | True Botch! -{botch}!"
        if specialty == True:
            message2 = f"Successes: {successes}, Botches: {botch}, \x02\x1FTotal: {total + ten}\x0F | Added {ten} from specialty."

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
