import re
import sys

keywords = ['else', 'if', 'int', 'return', 'void', 'while']


def determineCurrWord(word):
    try:
        int(word)
        print("Num: " + word)
    except ValueError:
        if word in keywords:
            print("Keyword: " + word)
        else:
            print("ID: " + word)


def lexer(filename):
    inputFile = open(filename, 'r')
    lookAheadChars = ['<', '>', '=', '/', '*', '!']
    validTwoChars = ['<=', '>=', '!=', '==', '/*', '*/', '//']
    comment = False  # boolean to determine if block comment is on
    for line in inputFile:
        currWord = ''
        deuceChars = ''
        if line.strip() != '':
            print("\nInput: " + line.strip())
            for char in line:
                if (
                        re.fullmatch(r'[a-zA-Z0-9+\-*/<=>!;,(){}\[\]\s]*',
                                     char)):  # check if the char has a invalid character
                    if (re.fullmatch(r'[a-zA-Z0-9]', char)):
                        currWord += char
                        if (deuceChars != ''):
                            if comment is False:
                                printChar = deuceChars.strip()
                                if (printChar == '!'):
                                    print("Error: " + printChar)
                                elif (printChar != ''):
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
                                    # print('comment started')
                                elif deuceChars == '*/' and comment is True:
                                    comment = False
                                    # print('comment stopped')
                                elif deuceChars == '//':  # inline comment
                                    break
                                else:
                                    if comment is False:
                                        printChar = deuceChars.strip()
                                        if (printChar != ''):
                                            print(printChar)
                                deuceChars = ''
                            else:
                                if comment is False:
                                    printChar = deuceChars[0].strip()
                                    if printChar == '!':
                                        print('Error: ' + printChar)
                                    elif (printChar != ''):
                                        print(printChar)
                                deuceChars = deuceChars[1]
                        else:  # will take care of the spaces
                            if (deuceChars != ''):
                                if comment is False:
                                    printChar = deuceChars.strip()
                                    if (printChar == '!'):
                                        print("Error: " + printChar)
                                    elif (printChar != ''):
                                        print(printChar)
                                deuceChars = ''
                            if comment is False:
                                printChar = char.strip()
                                if (printChar == '!'):
                                    print('Error: ' + printChar)
                                elif (printChar != ''):
                                    print(char.strip())
                else:
                    if comment is False:
                        print('Error: ' + currWord + char)
                    currWord = ''


lexer(sys.argv[1])
