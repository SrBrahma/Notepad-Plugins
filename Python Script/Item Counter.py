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
# As I made this code firstly for myself and I don't intend to use it constantly, the code is very rudimentary. But works well.
#
#
#
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


# ========== SETTINGS =============
#
# Will add zeroes to the left until X chars (0 disables)
# The prefix is not counted on the X chars.
ZEROES_ON_LEFT_UNTIL_X_CHARS = 2
#
# "0x", etc to be written before the number
COUNTER_PREFIX = ""
#
# Numeric base (%x = hexadecimal (lowercase), "%X = hexadecimal (Uppercase), %d = decimal, %o = octal)
NUMERIC_BASE = "%x"
#
# Start counting from this value
DEFAULT_STARTING_VALUE = 0
#
# =================================


def match_found(m):
    global foundMatch
    global previousStartPosition
    global actualCustomLine
    foundMatch = 1

    # startEnd is a tuple; = (start, end)
    startEnd = m.span(0)
    
    if chr(editor.getCharAt(startEnd[0])) == "F":
        actualCustomLine = int(editor.getTextRange(startEnd[0]+2, startEnd[1] - 1), 16) + 1 # Get the inner value and make it a integer, and add 1
    else:
        willWrite = COUNTER_PREFIX + (NUMERIC_BASE % actualCustomLine).zfill(ZEROES_ON_LEFT_UNTIL_X_CHARS)
        if editor.getTextRange(startEnd[0]+1, startEnd[1] - 1) != willWrite: # Reduced the time a lot if content is equal to what is going to be written
            editor.deleteRange(startEnd[0]+1, startEnd[1] - startEnd[0] - 2) # Deletes the content inside the brackets []
            editor.insertText(startEnd[0]+1, willWrite) 
        actualCustomLine += 1
        
    previousStartPosition = startEnd[0] + 2 # Make the searcher don't look for the same line indicator when having a F[] before.
    
    
editor.beginUndoAction() # To undo everything with a single ctrl+z


actualCustomLine = DEFAULT_STARTING_VALUE

previousStartPosition = 0

foundMatch = 1
while foundMatch:
    foundMatch = 0
    editor.research('F?\[\w*\]', match_found, 0, previousStartPosition, 0, 1)

editor.endUndoAction() # To undo everything with a single ctrl+z
