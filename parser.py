# Assume the test file is lexically correct
import lexer

tokenList = lexer.tokenList
tokenList.append("$")  # todo verify if this needs to be done or not
tokenIndex = -1
currToken = ''


def nextToken():
    global tokenIndex, currToken
    tokenIndex = tokenIndex + 1
    try:
        currToken = tokenList[tokenIndex]
    except IndexError:
        print("ERROR: end of token list")  # Should not call the method. The grammar should be accepted on the last "$"

# def program():
#     declarationList()
