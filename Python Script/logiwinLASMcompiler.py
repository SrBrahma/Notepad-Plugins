# LASM (Logiwin Assembly) compiler
# Written to be used with Python Script, Notepad++
# By Henrique Bruno Fantauzzi de Almeida, Rio de Janeiro - RJ - Brazil
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

# only a debugging func
def p(var, text):
    console.write(text+" = {" + str(var) + "}\n")
    
from Npp import *
import itemCounter
import multipleReplacer
    
# Used on the jumps, as the address may not be represented in fully FFFFFF form.
FILL_ZEROES_UNTIL_X_CHARS = 6

# Following the basic Logisim format mode
MAX_DATA_PER_LINE = 8
#
# Logisim default value
STREAKS_TO_GROUP = 4

def getReSpan(m):
    global globalReSpan
    globalReSpan = m.span()
    
def getReGroupContent(m):
    global globalReGroup
    globalReGroup = m.groups()[0]
    
def localLabelCallerMatch(m):
    global localLabelFound
    global globalReGroup
    global globalQuitExecution
    global globalReSpan
    
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
        
    globalReGroup = False
    # Gets the local label Address
    editor.research(m.groups()[1] + ":\s*\[(\w+)", getReGroupContent, 0, globalReSpan[1], 0, 1)
    if not globalReGroup:
        globalQuitExecution = True
        errorString = ("ERROR 2: No local label called by \"" + m.group() + "\" was found. Local labels must be below global labels.\n")
        console.write(errorString)
        notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
        return
        
    return m.groups()[0] + "#0x" + globalReGroup.zfill(FILL_ZEROES_UNTIL_X_CHARS)

def globalLabelCallerMatch(m):
    global globalReGroup
    
    globalReGroup = False
    # Gets the global label Address
    editor.research(m.groups()[1] + ":\s*\[(\w+)", getReGroupContent)
    if not globalReGroup:
        globalQuitExecution = True
        errorString = ("ERROR 3: No global label called by \"" + m.group() + "\" was found.\n")
        console.write(errorString)
        notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
        return
        
    return m.groups()[0] + "#0x" + globalReGroup.zfill(FILL_ZEROES_UNTIL_X_CHARS)


    
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
        editor.addText(str(timesToWrite)+"*"+contentToWrite)
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
    errorString = ("ERROR 1: Final Address [" + m.groups()[0] + "] holds a value (\"" + m.groups()[1] + "\") of length "
                        + str(len(m.groups()[1])) + " (expected length of 8 chars). Probably a invalid data that couldn't be"
                       " converted, or a too big number.\n")
    console.write(errorString)
    notepad.messageBox(errorString, "LogiwinLasmConverter", 0)
    
def errorBoxInvalidStringLength(m):
    global globalQuitExecution
    globalQuitExecution = True
    errorString = ("ERROR 2: Final Address [" + m.groups()[0] + "] holds a string (\"" + m.groups()[1] + "\") of length "
                        + str(len(m.groups()[1])) + " (expected a maximum length of 4 chars).\n")
    console.write(errorString)
    notepad.messageBox(errorString, "LogiwinLasmConverter", 0)

    
    
    
    
    
    
def main():
    
    global globalQuitExecution
    globalQuitExecution = False
    
    editor.beginUndoAction() # To undo everything with a single ctrl+z

    # Make sure the Addresses are right
    itemCounter.main()

    # Remove commentaries
    editor.rereplace(";.*", "")

    # Remove any spaces after (convertDecDataTo32Bits uses $ operator)
    editor.rereplace("\s+$", "")
    
    # Remove any spaces before
    editor.rereplace("^\s+", "")
    
    # Convert local labels callers
    editor.rereplace('(.+)(\.\w+\\b)(?![:"])', localLabelCallerMatch)
    if globalQuitExecution:
        return
    
    # Convert global labels callers
    editor.rereplace('(.+)(_\w+\\b)(?![:"])', globalLabelCallerMatch)
    if globalQuitExecution:
        return

    # Convert decimal data to 32 bits
    editor.rereplace("(\]\s*)(?:0d)?(\d+)d?$", lambda m: m.groups()[0] + ("%X" % int(m.groups()[1])).zfill(8))
    # Convert hexadecimal data to 32 bits
    editor.rereplace("(\]\s*)0x(\w{1,7})", lambda m: m.groups()[0] + m.groups()[1].zfill(8))

    # Converts the instructions to hexadecimal machine code form
    multipleReplacer.main()

    # Search for any content with more or less than 8 digits
    editor.research("\[(\w+)\]\s*(\w{0, 7}|\w{8}\w+)$", errorBoxInvalidDataLength, 0, 0, 0, 1)
    if globalQuitExecution:
        return
    
    # Removes labels
    editor.rereplace('[\._]\w+:', "")
    
    #Remove Empty Lines (https://stackoverflow.com/a/39282395 didnt use it actually it was bad)
    editor.rereplace("^\s*\r\n", "")
    
    # Search for any string with more than 4 chars
    editor.research("\[(\w+)\]\s*(\"(.{4}.+)\")$", errorBoxInvalidStringLength, 0, 0, 0, 1)
    if globalQuitExecution:
        return
    
    # Converts string data to 
    editor.rereplace('"(.*)"', convertLogiwinString)

    # Initialize the list
    contentList = []
    
    # Seach for any invalid data: non-hex digits and/or not 8 digits
    editor.research("\[(\w+)\]\s*$", errorBoxInvalidStringLength, 0, 0, 0, 1)
    
    # Get the [Address] and its content, and append them to the contentList[]
    editor.research("\[(\w+)\]\s*(\w+)", lambda m: contentList.append((int(m.groups()[0], 16), m.groups()[1])))

    # Put them in ascending order, according to Address
    contentList = sorted(contentList, key = lambda value: value[0])

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