# LASM (Logiwin Assembly) compiler
# Written to be used with Python Script, Notepad++
# By Henrique Bruno Fantauzzi de Almeida, Rio de Janeiro - RJ - Brazil
#   (aka SrBrahma!)
# Code to convert LASM language files to Logisim RAM/ROM text type. Used on my Logiwin project.
#
# Data like 0x1 and 0xE4 are automatically transformed to 00000001 and 000000E4
# Addresses in brackets should be in hexadecimal.
# Decimal data can be XXXX (ex 42), YYYYd (ex 934d) and 0dZZZZ (ex 0d32). 
# The latter form is suggested, since it prevents possible mistakes

# Error search to do:
# 1) strings with > 4 chars
# 2) invalid data
# 3) same address
# 4) label to jump doesn't exists
# 5) same label name

# only a debugging func
def p(var, text):
    console.write(text+" = {" + str(var) + "}\n")
    
from Npp import *
import itemCounter
import multipleReReplacer
    
# Used on the jumps, as the address may not be represented in fully FFFFFF form.
FILL_ZEROES_UNTIL_X_CHARS = 6
#
# Following the basic Logisim format mode
MAX_DATA_PER_LINE = 8
#
# Logisim default value
STREAKS_TO_GROUP = 4
#
# Don't initialize this Address content, useful for assigning volatile variables.
WONT_COMPILE_WITH_ADDRESS_PREFIX = "V"
#
# Fixed Address prefix
FIXED_ADDRESS_PREFIX = "F"


def getReSpan(m):
    global globalReSpan
    globalReSpan = m.span()
    
def getReGroups0(m):
    global globalReGroups
    globalReGroups = m.groups()[0]
    
def getReGroupsList(m):
    global globalReGroupsList
    globalReGroupsList = m.groups()
    
def localLabelCallerMatch(m):
    global globalReGroups
    global globalQuitExecution
    global globalReSpan
    
    if not globalQuitExecution:
        # startEnd is a tuple; = (start, end)
        startEnd = m.span()
        
        globalReSpan = False
        # Gets the previous global label position
        editor.research('_\w+:', getReSpan, 0, 0, startEnd[1]) # As it can find multiple results, the last result will be the closest to the startEnd[1]
        # If don't find any previous labels
        if not globalReSpan:
            globalQuitExecution = True
            errorString = ("ERROR 1: No global label found before the line \"" + m.group() + "\". Local labels must be below global labels.\n")
            console.write(errorString)
            notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
            return
            
        globalReGroups = False
        # Gets the local label Address
        editor.research(m.groups()[1] + ":\s*\[(\w+)", getReGroups0, 0, globalReSpan[1], 0, 1)
        if not globalReGroups:
            globalQuitExecution = True
            errorString = ("ERROR 2: No local label called by \"" + m.group() + "\" was found. Check for missing \":\" after label definition. Also, local labels must be below global labels.\n")
            console.write(errorString)
            notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
            return m.group()
            
        return m.groups()[0] + "#0x" + globalReGroups.zfill(FILL_ZEROES_UNTIL_X_CHARS)
        
    else:
        return m.group()

def globalLabelCallerMatch(m):
    global globalReGroups
    global globalQuitExecution
    
    if not globalQuitExecution:
        globalReGroups = False
        # Gets the global label Address
        editor.research(m.groups()[1] + ":\s*\[(\w+)", getReGroups0)
        if not globalReGroups: # If didn't find the global label
            globalQuitExecution = True
            errorString = ("ERROR 3: No global label called by \"" + m.group() + "\" was found.\n")
            console.write(errorString)
            notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
            return m.group()
            
        return m.groups()[0] + "#0x" + globalReGroups.zfill(FILL_ZEROES_UNTIL_X_CHARS)
    else:
        return m.group()

def translateVariableName(m):
    global globalReGroups
    global globalQuitExecution
    global globalReSpan

    
    if not globalQuitExecution:
        # startEnd is a tuple; = (start, end)
        startEnd = m.span()
        
        globalReSpan = False
        # Gets the previous global label
        editor.research('_\w+:', getReSpan, 0, 0, startEnd[1]) # As it can find multiple results, the last result will be the closest to the startEnd[1]
        # If don't find any global labels before,
        if not globalReSpan:
            globalQuitExecution = True
            errorString = ("ERROR 4: No global label found before the line \"" + m.group() + "\". Variables must be called after global variables definitions.\n")
            console.write(errorString)
            notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
            return
            
        stopLookingAtPos = globalReSpan[0]
        
        # Now will look for another label before it, but not named _local.
        editor.research('(?!_local:)_\w+:', getReSpan, 0, 0, startEnd[1]) # As it can find multiple results, the last result will be the closest to the startEnd[1]
        # If no label found...
        if not globalReSpan:
            startingLookingAt = 0
            
        else:
            startingLookingAt = globalReSpan[1]
            
        # m.groups()[0] = address, m.groups()[1] = &, m.groups()[2] = variable
        
        globalReGroups = False
        # Gets the local label Address
        editor.research("(?:_local:)[\s\S]*" + m.groups()[2] + ":\s*[\[\{](\w+)[\]\}]", getReGroups0, 0, startingLookingAt, stopLookingAtPos, 1)
        if not globalReGroups:
        
            # if variable not found in global range, look in global range
            globalReGroups = False
            editor.research("(?:_global:)[\s\S]*" + m.groups()[2] + ":\s*[\[\{](\w+)[\]\}]", getReGroups0, 0, 0, 0, 1)
            if not globalReGroups:
                globalQuitExecution = True
                errorString = ("ERROR 5: No variable called by \"" + m.group() + "\" was found either on local or global labels.\n")
                console.write(errorString)
                notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
                return m.group()
            
        if m.groups()[1]: # If & before the variable name, replace with #
            return m.groups()[0] + "#" + globalReGroups.zfill(FILL_ZEROES_UNTIL_X_CHARS)
        else:
            return m.groups()[0] + globalReGroups.zfill(FILL_ZEROES_UNTIL_X_CHARS)
        
    # if globalQuitExecution:
    else:
        return m.group()
        
def addOneAndNewlineOrSpace(counterData):
    counterData += 1
    if counterData >= MAX_DATA_PER_LINE:
        editor.addText("\n")
        counterData = 0
    else:
        editor.addText(" ")

    return counterData
    
def writeMemoryCode(contentToWrite, timesToWrite, counterData):
    if timesToWrite >= STREAKS_TO_GROUP:
        editor.addText(str(timesToWrite) + "*" + contentToWrite)
        counterData = addOneAndNewlineOrSpace(counterData)
    else:
        for counter in range(timesToWrite):
            editor.addText(contentToWrite)
            counterData = addOneAndNewlineOrSpace(counterData)
    return counterData
    
def convertLogiwinString(m):
    oldString = m.groups()[0]
    newString = ""
    for charIndex, char in enumerate(oldString):
        newString += "%X" % ord(char)
    for charIndex in range(charIndex, 3):
        newString += "00"
    return newString

def errorBoxInvalidDataLength(m):
    global globalQuitExecution
    globalQuitExecution = True
    errorString = ("ERROR 6: Final Address [" + m.groups()[0] + "] holds a value (\"" + m.groups()[1] + "\") of length "
                        + str(len(m.groups()[1])) + " (expected length of 8 hexadecimal chars). Probably a invalid data or instruction that couldn't be"
                       " converted, or a too big number. (Did you forgot # or & before the instruction argument, that requires it?)\n")
    console.write(errorString)
    notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
    
def errorBoxInvalidStringLength(m):
    global globalQuitExecution
    globalQuitExecution = True
    errorString = ("ERROR 7: Final Address [" + m.groups()[0] + "] holds a string (\"" + m.groups()[1] + "\") of length "
                        + str(len(m.groups()[1])) + " (expected a maximum length of 4 chars).\n")
    console.write(errorString)
    notepad.messageBox(errorString, "LogiwinLasmConverter", 0)

    
    
    
    
    
    
def main():
    
    global globalQuitExecution
    global foundMatch
    globalQuitExecution = False
    
    editor.beginUndoAction() # To undo everything with a single ctrl+z

    # Remove commentaries
    editor.rereplace(";.*", "")
    
    # Make sure the Addresses are right
    if itemCounter.main(): # If error found,
        editor.endUndoAction()
        return
    
    # Variables
    if itemCounter.main("{", "}", 0x400000): # If error found,
        editor.endUndoAction()
        return
        
    # Removes the F from F[] and F{}
    editor.rereplace("F(?=\[\w+\]|F\{\w+\})", "")
    
    # Remove any spaces after
    editor.rereplace("[ \t]+$", "")
    # Remove any spaces before
    editor.rereplace("^[ \t]+", "")
    
    
    # Convert decimal instruction argument to 6 hex digits
    editor.rereplace("(\]\s*\S+\s+[#&]?)(?:0d)?(\d+)d?$", lambda m: m.groups()[0] + ("%X" % int(m.groups()[1])).zfill(6))
    # Convert hexadecimal instruction argument to 6 hex digits (if was less), also remove "0x"
    editor.rereplace("(\]\s*\S+\s+[#&]?)0x(\w{1,6}\\b)", lambda m: m.groups()[0] + m.groups()[1].zfill(6))
    # Convert decimal data to 8 hex digits
    editor.rereplace("(\]\s*)(?:0d)?(\d+)d?$", lambda m: m.groups()[0] + ("%X" % int(m.groups()[1])).zfill(8))
    # Convert hexadecimal data to 8 hex digits (if was less), also remove "0x"
    editor.rereplace("(\]\s*)0x(\w{1,8})", lambda m: m.groups()[0] + m.groups()[1].zfill(8))
    
    # Search for any string with more than 4 chars
    editor.research("\[(\w+)\]\s*(\"(.{4}.+)\")$", errorBoxInvalidStringLength, 0, 0, 0, 1)
    if globalQuitExecution:
        editor.endUndoAction()
        return
    
    # Converts string data to 
    editor.rereplace('"(.*)"', convertLogiwinString)
    
    
    # Convert variables callers
    # m.groups()[0] = address, m.groups()[1] = &, m.groups[2] = variable
    editor.rereplace("(\[.*?\][ \t]*\w+[ \t]+)(&)?([a-zA-Z]\w+\\b)", translateVariableName)
    if globalQuitExecution:
        editor.endUndoAction()
        return
    
    # Remove variables labels and definers
    # editor.rereplace("(_local:|_global\s", "")
    
    # Convert local labels callers
    editor.rereplace('(.+)(\.\w+\\b)(?![:"])', localLabelCallerMatch)
    if globalQuitExecution:
        editor.endUndoAction()
        return
        
    # Convert global labels callers
    editor.rereplace('(.+)(_\w+\\b)(?![:"])', globalLabelCallerMatch)
    if globalQuitExecution:
        editor.endUndoAction()
        return
    
    # Converts the instructions to hexadecimal machine code form
    if multipleReReplacer.main(): # if error found,
        editor.endUndoAction()
        return


    # Search for any data with more or less than 8 digits
    editor.research("\[(\w+)\]\s*(\w{1, 7}\\b|\w{8}\w+|\s*$)", errorBoxInvalidDataLength, 0, 0, 0, 1)
    if globalQuitExecution:
        editor.endUndoAction()
        return


    # Initialize the list
    contentList = []
    
    # Seach for any invalid data: non-hex digits and/or not 8 digits
    editor.research("\[(\w+)\]\s*$", errorBoxInvalidStringLength, 0, 0, 0, 1)
    if globalQuitExecution:
        editor.endUndoAction()
        return
        
    # Get the [Address] and its content, and append them to the contentList[]
    editor.research("\[(\w+)\]\s*(\w+)", lambda m: contentList.append((int(m.groups()[0], 16), m.groups()[1], m.start(0))))
    
    
        
    # Put them in ascending order, according to Address
    contentList = sorted(contentList, key = lambda value: value[0])
    
    # Look for already existing Address
    for index, content in enumerate(contentList[1:], start = 1):
        if content[0] == contentList[index - 1][0]:
            errorString = ("ERROR 6: Same address found:\n"
                           "Line " + str(editor.lineFromPosition(content[2])) + ": [" + str(content[0]) + "]\n"
                           "Line " + str(editor.lineFromPosition(contentList[index - 1][2])) + ": [" + str(contentList[index - 1][0]) + "]\n")
            console.write(errorString)
            notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
            return
        
    # Adds a different value, to push the last value (to work with the below for)
    contentList.append((contentList[len(contentList)-1][0], "XXX"))

    # Erase all the text on file
    editor.clearAll() 

    # writes the file header
    editor.addText("v2.0 raw\n")
    
    # Initialize variables
    previousAddress = contentList[0][0]
    previousContent = contentList[0][1]
    sameContentStreak = 1
    counterData = 0
    
    # Write the content on the file
    for contentIndex, content in enumerate(contentList[1:], start = 1):

        # if jumped over blank addresses
        if content[0] > previousAddress + 1:
            if previousContent == "00000000":
                if content[1] == "00000000":
                    sameContentStreak += (content[0] - previousAddress)
                
                # If actual content is different, write the zeroes from the blank space and old zero streak
                else:
                    counterData = writeMemoryCode("0", sameContentStreak + (content[0] - previousAddress) - 1, counterData)
                    sameContentStreak = 1
                    
            # If previous content is not zero, them write them
            else:
                counterData = writeMemoryCode(previousContent, sameContentStreak, counterData)
                
                # If actual content is zero, sameContentStreak = blank spaces + this one
                if content[1] == "00000000":
                    sameContentStreak = (content[0] - previousAddress)
                    
                # Else, write the zeroes from the blank space
                else:
                    counterData = writeMemoryCode("0", content[0] - previousAddress - 1, counterData)
                    sameContentStreak = 1
            
        # If actual content is the same of previous content
        elif content[1] == previousContent:
            sameContentStreak += 1
        
        # if content is diferent from previous address
        else:
            counterData = writeMemoryCode(previousContent, sameContentStreak, counterData)
            sameContentStreak = 1

        previousAddress = content[0]
        previousContent = content[1]
    # End of the for loop
    
    
    editor.endUndoAction() # To undo everything with a single ctrl+z

if __name__ == "__main__":
    main()