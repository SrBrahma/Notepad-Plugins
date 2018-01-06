from Npp import *
#
# ItemCounterV1
# For Python Script, Notepad++
#
# By Henrique Bruno Fantauzzi de Almeida, Rio de Janeiro - RJ - Brazil
# Github: https://github.com/SrBrahma/NotepadPlusPlus-Plugins
# 03/01/2018
#
# A small and simple code to count and write items or lines in decimal, hexadecimal or octal in a text.
# To make it write the counter, add brackets ("[]") anywhere on text and it will count starting from zero (default).
# You can write a "F" before the brackets to make the value fixed, and the next value will be normally incremented by 1.
# Has an automatic zero fill function, which will make all counted values with the same length.
# As I made this code firstly for myself and I don't intend to use it constantly, the code is very rudimentary. But works well.
#
# Example:
#  [0x00]  Lorem ipsum dolor sit amet, 
#  [0x01]  consectetur adipiscing elit, sed do eiusmod 
# F[0xF7]  tempor incididunt ut labore et 
#  [0xF8]  dolore magna aliqua. Lectus arcu bibendum at
#  [0xF9]  varius vel pharetra vel. Scelerisque
# F[0x03]  fermentum dui faucibus in ornare quam
#  [0x04]  viverra. Blandit turpis cursus in hac
#  [0x05]  habitasse platea. Posuere lorem ipsum
#def p(var, text):
#    console.write(text+" = {" + str(var) + "}\n")
    
# ========== SETTINGS =============
#
# "0x", etc to be written before the number
COUNTER_PREFIX = ""
#
# Numeric base (%x = hexadecimal (lowercase), "%X = hexadecimal (Uppercase), %d = decimal, %o = octal)
NUMERIC_BASE = "%X"
#
# Add prefix to fixed values, if it don't already have it
ADD_PREFIX_FIXED_VALUES = True
#
# Automatic get the maximum counter length and use it to format all values {
AUTOMATIC_LENGTH_ZERO_FILL = True
# 
# Zero fill the fixed value? (NOTE: For this to happen, the fixed value must contain the 
#  prefix specified (ADD_PREFIX_FIXED_VALUES = True do this automatically)
# ( If AUTOMATIC_LENGTH_ZERO_FILL is False, will use ZEROES_ON_LEFT_UNTIL_X_CHARS value)
# ( Also, if AUTOMATIC_LENGTH_ZERO_FILL is true, will remove any excessive zeroes fill of fixed values)
ZERO_FILL_FIXED_VALUES = True
#
#
# Manual zero fill
# Will add zeroes to the left until X chars (0 disables)
# The prefix is not counted on the X chars.
ZEROES_ON_LEFT_UNTIL_X_CHARS = 0
#
# Start counting from this value, when no previous fixed value is set
DEFAULT_STARTING_VALUE = 0
#
# 
# =================================
    
def main():
    global globalQuit
    globalQuit = False
    
    try:
        def match_found(m):
            global foundMatch
            global previousStartPosition
            global actualCustomLine
            foundMatch = True
            # startEnd is a tuple; = (start, end)
            startEnd = m.span(0)
            #try:
            if m.groups()[0] == "F":
                if NUMERIC_BASE == "%X" or NUMERIC_BASE == "%x":
                    actualCustomLine = int(editor.getTextRange(startEnd[0]+2, startEnd[1] - 1), 16) + 1 # Get the inner value and make it a integer, and add 1
                if NUMERIC_BASE == "%d":
                    actualCustomLine = int(editor.getTextRange(startEnd[0]+2, startEnd[1] - 1)) + 1 # Get the inner value and make it a integer, and add 1
                if NUMERIC_BASE == "%o":
                    actualCustomLine = int(editor.getTextRange(startEnd[0]+2, startEnd[1] - 1), 8) + 1 # Get the inner value and make it a integer, and add 1
            #except:
                #pass
               # notepad.messageBox("Error 1: Invalid fixed number , "itemCounter", 0) Editor.lineFromPosition(pos)
            else:
                willWrite = COUNTER_PREFIX + (NUMERIC_BASE % actualCustomLine).zfill(ZEROES_ON_LEFT_UNTIL_X_CHARS)
                if  m.groups()[1] != willWrite: # Reduced the time a lot if content is equal to what is going to be written
                    editor.deleteRange(startEnd[0]+1, startEnd[1] - startEnd[0] - 2) # Deletes the content inside the brackets []
                    editor.insertText(startEnd[0]+1, willWrite) 
                actualCustomLine += 1
                
            previousStartPosition = startEnd[0] + 2 # Make the searcher don't look for the same line indicator when having a F[] before.
            
        editor.beginUndoAction() # To undo everything with a single ctrl+z

        actualCustomLine = DEFAULT_STARTING_VALUE

        global previousStartPosition
        previousStartPosition = 0
        
        global foundMatch
        foundMatch = True
        while foundMatch:
            foundMatch = False
            editor.research("(F?)\[(\w*)\]", match_found, 0, previousStartPosition, 0, 1)
            
        
        
        # Add prefix to fixed values, if they haven't
        if ADD_PREFIX_FIXED_VALUES and COUNTER_PREFIX:
            editor.rereplace("(?<=F\[)(?!" + COUNTER_PREFIX + ")(?=.*\])", COUNTER_PREFIX)
           
        def findLargestLength(m):
            global globalLongestLength
            if len(m.groups()[0]) > globalLongestLength:
                globalLongestLength = len(m.groups()[0])
      
        if AUTOMATIC_LENGTH_ZERO_FILL:
            # First get the maximum length
            global globalLongestLength
            globalLongestLength = 0

            # The longest length is the valid length, excludes the zeroes before
            editor.research("(?<=\[)(?:" + COUNTER_PREFIX + ")?0*(\w*)(?=\])", findLargestLength)
            # Now replace all the values with a length smaller
            # Get the largest length, excluding already existing zero fills
            
            if ZERO_FILL_FIXED_VALUES:
                # Replaces all
                editor.rereplace("(?<=\[" + COUNTER_PREFIX + ")(\w{0, " + str(globalLongestLength - 1) + "})(?=\])", lambda m: m.group().zfill(globalLongestLength))
            
                # Remove possible excessive zeroes from fixed values (from previous executions that zero filled them more than they need now)
                editor.rereplace("(?<=F\[)0+(\w{" + str(globalLongestLength) + "})(?=\])", "\\1")
            
            else:
                # Only replaces non-fixed values
                editor.rereplace("(?<!F\[" + COUNTER_PREFIX + ")(?<=\[" + COUNTER_PREFIX + ")(\w{0, " + str(globalLongestLength - 1) + "})(?=\])", lambda m: m.group().zfill(globalLongestLength))
                
        else:
            if ZERO_FILL_FIXED_VALUES:
                editor.rereplace("(?<=F\[" + COUNTER_PREFIX + ")(\w{0, " + str(ZEROES_ON_LEFT_UNTIL_X_CHARS - 1) + "})(?=\])", lambda m: m.group().zfill(ZEROES_ON_LEFT_UNTIL_X_CHARS))
        editor.endUndoAction() # To undo everything with a single ctrl+z
    except Exception as e:
        notepad.messageBox(e.message, "itemCounter", 0)

if __name__ == "__main__":
    main()
    