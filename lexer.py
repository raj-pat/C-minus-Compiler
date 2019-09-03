# This project file will read the input and would return the token information tp parser file.
# #pseudo code
# for each word
#         for each letter
#             if comment is off
#                 concatenate if the letter is [a-zA-Z] or [0-9]
#             else
#                     if letter is a space or any valid character
#                         check the concatenated var
#                         if it is a letter or a num
#                                 if keyword or id or num and return
#                             return the value of the key of the current char if its not space and is valid
#
#                     if letter is [0-9]
#                         maybe an error or not -> check the grammar
#         #when the word ends
#         check the concatenate word and determine if it's an id or a keyword or a num
#     else
#     return error for invalid symbol.

import re

keywords = ['else', 'if', 'int', 'return', 'void', 'while']
def lexer(filename):
    inputFile = open(filename, 'r')
    lookAheadChars = ['<', '>', '=', '/', '*', '!']
    validChars = {'(': '(', ')': ')', '{': '{', '}': '}', '[': '[', ']': ']', ';': ';', '*': 'mulop', '/': 'mulop',
                  '+': 'addop', '-': 'addop', '<': 'relop', '<=': 'relop', '>': 'relop', '>=': 'relop', '==': 'relop',
                  '!=': 'relop', '=': '=', '\,': '\,', '/*': 'n/a', '*/': 'n/a'}
    validTwoChars = ['<=', '>=', '!=', '==', '/*', '*/', '//']
    comment = False  # boolean to determine if block comment is on
    for line in inputFile:
        print("Input: " + line.strip())
        currWord = ''
        deuceChars = ''
        for char in line:
            if (re.fullmatch(r'[a-zA-Z0-9+\-*/<=>!;,(){}\[\]\s]*', char)):  # check if the char has a invalid character
                if (re.fullmatch(r'[a-zA-Z0-9]', char)):
                    currWord += char
                    if (deuceChars != ''):
                        if comment is False:
                            printChar = deuceChars.strip()
                            if (printChar != ''):
                                print(printChar)  # prints a single character
                        deuceChars = ''
                else:
                    if currWord != '':
                        if comment is False:
                            determineCurrWord(currWord)
                        currWord = ''
                    if (char in lookAheadChars and deuceChars == ''):
                        deuceChars += char  # concatenate the first character
                    elif (char in lookAheadChars and deuceChars != ''):
                        deuceChars += char
                        if deuceChars in validTwoChars:
                            if comment is False and deuceChars == '/*':
                                comment = True
                                print('comment started')
                            elif deuceChars == '*/' and comment is True:
                                comment = False
                                print('comment stopped')
                            elif deuceChars == '//':
                                # todo goto for loop perhaps?
                                print('in-line comment')
                            else:
                                if comment is False:
                                    printChar = deuceChars.strip()
                                    if (printChar != ''):
                                        print(printChar)
                            deuceChars = ''
                        else:
                            if comment is False:
                                printChar = deuceChars[0].strip()
                                if (printChar != ''):
                                    print(printChar)
                            deuceChars = deuceChars[1]
                    else:  # will take care of the spaces
                        if (deuceChars != ''):
                            if comment is False:
                                printChar = deuceChars.strip()
                                if (printChar != ''):
                                    print(printChar)
                            deuceChars = ''
                        if comment is False:
                            print(char.strip())
            else:
                if comment is False:
                    print('Error: ' + currWord + char)
                currWord = ''


def determineCurrWord(word):
    try:
        int(word)
        print("Num: " + word)
    except ValueError:
        if word in keywords:
            print("Keyword: " + word)
        else:
            print("ID: " + word)
lexer('test')
