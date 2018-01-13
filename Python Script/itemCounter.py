from Npp import *
import re
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
# The raw form
MARKER_BEFORE = "["
#
# The raw form
MARKER_AFTER = "]"
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

def main(markerBefore0 = MARKER_BEFORE, markerAfter0 = MARKER_AFTER, defaultStartingValue = DEFAULT_STARTING_VALUE):
    if 1 == 1:
        def foundMarkers(m):
            global globalActualCounter
            global globalQuit
            
            if not globalQuit:
                # [0] = Fixed, [1] = marker before, [2] = content, [3] = marker after
                groups = m.groups()
                try:
                    if m.groups()[0]: # If found fixed value
                        if NUMERIC_BASE == "%X" or NUMERIC_BASE == "%x":
                            globalActualCounter = int(groups[2], 16) + 1
                        if NUMERIC_BASE == "%d":
                            globalActualCounter = int(groups[2]) + 1 # Get the inner value and make it a integer, and add 1
                        if NUMERIC_BASE == "%o":
                            globalActualCounter = int(groups[2], 8) + 1 # Get the inner value and make it a integer, and add 1
                        return m.group()
                except:
                    console.write("itemCounter text error: Error on fixed counter \"" + m.group() + "\", on line " + str(editor.lineFromPosition(m.start())) + "\n")
                    notepad.messageBox("Error on fixed counter \"" + m.group() + "\", on line " + str(editor.lineFromPosition(m.start())) + "\n", "itemCounter", 0)
                    editor.endUndoAction()
                    globalQuit = 1
                    return m.group()
                   # notepad.messageBox("Error 1: Invalid fixed number , "itemCounter", 0) Editor.lineFromPosition(pos)
                else:
                    willWrite = groups[0] + groups[1] + COUNTER_PREFIX + (NUMERIC_BASE % globalActualCounter).zfill(ZEROES_ON_LEFT_UNTIL_X_CHARS) + groups[3]
                    globalActualCounter += 1
                    return willWrite
            else:
                return m.group()
                
        global globalQuit
        global globalActualCounter
        global markerBefore
        global markerAfter
                
        globalQuit = 0
        globalActualCounter = defaultStartingValue
        markerBefore = re.escape(markerBefore0) # If the marker is a escape sequence, make it literal
        markerAfter = re.escape(markerAfter0)   # If the marker is a escape sequence, make it literal
        
        # end of foundMarkers
        editor.beginUndoAction() # To undo everything with a single ctrl+z
        
        # [0] = Fixed, [1] = marker before, [2] = content, [3] = marker after
        editor.rereplace("(F?)(" + markerBefore + ")(\w*)(" + markerAfter + ")", foundMarkers)
        if globalQuit:
            return 1
            
        # Add prefix to fixed values, if they haven't
        if ADD_PREFIX_FIXED_VALUES and COUNTER_PREFIX:
            editor.rereplace("(?<=F" + markerBefore + ")(?!" + COUNTER_PREFIX + ")(?=.*" + markerAfter + ")", COUNTER_PREFIX)
           
        def findLargestLength(m):
            global globalLongestLength
            if len(m.groups()[0]) > globalLongestLength:
                globalLongestLength = len(m.groups()[0])
      
        if AUTOMATIC_LENGTH_ZERO_FILL:
            # First get the maximum length
            global globalLongestLength
            globalLongestLength = 0

            # The longest length is the valid length, excludes the zeroes before
            editor.research("(?<=" + markerBefore + ")(?:" + COUNTER_PREFIX + ")?0*(\w*)(?=" + markerAfter + ")", findLargestLength)
            # Now replace all the values with a length smaller
            # Get the largest length, excluding already existing zero fills
            
            if globalLongestLength:
                if ZERO_FILL_FIXED_VALUES:
                    # Replaces all
                    editor.rereplace("(?<=" + markerBefore + COUNTER_PREFIX + ")(\w{0, " + str(globalLongestLength - 1) + "})(?=" + markerAfter + ")", lambda m: m.group().zfill(globalLongestLength))
                
                    # Remove possible excessive zeroes from fixed values (from previous executions that zero filled them more than they need now)
                    editor.rereplace("(?<=F" + markerBefore + ")0+(\w{" + str(globalLongestLength) + "})(?=" + markerAfter + ")", "\\1")
                
                else:
                    # Only replaces non-fixed values
                    editor.rereplace("(?<!F" + markerBefore + COUNTER_PREFIX + ")(?<=" + markerBefore + COUNTER_PREFIX + ")(\w{0, " + str(globalLongestLength - 1) + "})(?=" + markerAfter + ")", lambda m: m.group().zfill(globalLongestLength))
                
        else:
            if ZERO_FILL_FIXED_VALUES:
                editor.rereplace("(?<=F" + markerBefore + COUNTER_PREFIX + ")(\w{0, " + str(ZEROES_ON_LEFT_UNTIL_X_CHARS - 1) + "})(?=" + markerAfter + ")", lambda m: m.group().zfill(ZEROES_ON_LEFT_UNTIL_X_CHARS))
        editor.endUndoAction() # To undo everything with a single ctrl+z
        return 0
        '''
    except Exception as e:
        console.write("itemCounter Python error (bad code): " + e.message)
        notepad.messageBox("(Bad code): " + e.message, "itemCounter Python error", 0)
        editor.endUndoAction()
        return 1'''
if __name__ == "__main__":
    main()
    