from Npp import *
#
# ItemCounterV1
# For Python Script, Notepad++
#
# By Henrique Bruno Fantauzzi de Almeida, Rio de Janeiro - RJ - Brazil
# Github: https://github.com/SrBrahma/NotepadPlusPlus-Plugins
# 03/01/2018
#
# Replaces multiple expressions on a text file using a dictionary file.
# Quotation marks can be used to define the expressions having spaces/tabs
# "\" can be used before the quotation mark to make it part of the text.
# 
# Based on this answer from Stack Overflow: https://stackoverflow.com/a/16197147
# The code is rudimentary and simple, but I made for personal use and does what is suposed to.
# Would be a lot simpler and faster with Regex.
#
# Example of content in the dictionary file:
# #; This is a default commentary in dictionary file. Only valid when in the start of a line (but can have spaces/tabs before)
# "original expression0" final0
# original final
# "original" "final expression"

def main():
    # ========== SETTINGS =============
    #
    # The commentary prefix in the dictionary file.
    COMMENT_PREFIX = "#;"
    #
    # Dictionary full path
    DICTIONARY_FULL_PATH = 'D:\Dictionary.txt'
    #
    # =================================

    COMMENT_PREFIX_LEN = len(COMMENT_PREFIX)

    editor.beginUndoAction() # To undo everything with a single ctrl+z

    with open(DICTIONARY_FULL_PATH) as file:

        for lineNumber, line in enumerate(file):
            # First remove any space/tab/etcs before text
            line = line.lstrip()
            
            # Now checks if the line is a commentary
            
            if not (len(line) >= COMMENT_PREFIX_LEN and line[:COMMENT_PREFIX_LEN] == COMMENT_PREFIX):
                lineContent = line.split()

                if len(lineContent) == 1:
                    notepad.messageBox("ERROR 1: Only 1 word found on line " + str(lineNumber) + " of the dictionary file.\n(" + lineContent[0] + ")", "Multiple Replacer.py", 0)
                    break
                    
                elif len(lineContent) > 1:
                
                    if lineContent[0][0] == '"':
                        firstStartedWithQuotes = True
                        startOfFirstExpression = 1
                    else:
                        firstStartedWithQuotes = False
                        startOfFirstExpression = 0
                        
                    isFirstExpression = True
                    secondStartedWithQuotes = False
                    endOfFirstExpression = 0
                    startOfSecondExpression = 0
                    endOfSecondExpression = 0
                    previousChar = ""
                    
                    for charIndex, char in enumerate(line[1:], start = 1):
                        
                        if char == " ":
                            # End of first non-quoted expression
                            if not firstStartedWithQuotes and isFirstExpression:
                                endOfFirstExpression = charIndex
                                isFirstExpression = False
                                
                            if not isFirstExpression and not secondStartedWithQuotes and not endOfSecondExpression and startOfSecondExpression:
                                endOfSecondExpression = charIndex
                                
                        # End of second expression / end of line
                        elif (char == "\n" or char == "\r" ) and not endOfSecondExpression:
                            endOfSecondExpression = charIndex
                            
                        elif char == '"' and previousChar != "\"":
                        
                            # End of second quoted expression
                            if secondStartedWithQuotes and not endOfSecondExpression:
                                endOfSecondExpression = charIndex
                                
                            # Start of second quoted expression
                            if not isFirstExpression and not endOfSecondExpression:
                                startOfSecondExpression = charIndex + 1
                                secondStartedWithQuotes = True
                                
                            # End of first quoted expression
                            if firstStartedWithQuotes and isFirstExpression:
                                endOfFirstExpression = charIndex
                                isFirstExpression = False
                                
                        # If another char        
                        else:
                            if not isFirstExpression and not startOfSecondExpression:
                                startOfSecondExpression = charIndex
                                secondStartedWithQuotes = False


                        previousChar = char
                    
                    # End of char loop
                    
                        # If not not found a second expression, display error
                    if not startOfSecondExpression:
                        notepad.messageBox("ERROR 2: Only 1 word found on line " + str(lineNumber) + " of the dictionary file.\n(" + lineContent[0] + ")", "Multiple Replacer.py", 0)
                        break
                        
                    if not endOfSecondExpression: 
                        endOfSecondExpression = charIndex + 1
                        
                    editor.replace(line[startOfFirstExpression:endOfFirstExpression], line[startOfSecondExpression:endOfSecondExpression])
                # End of more than one word conditional
            # End of not a commentary conditional
        # End of line loop      
    #)

    editor.endUndoAction() # To undo everything with a single ctrl+z

if __name__ == "__main__":
    main()