# Assume the test file is lexically correct
import lexer

tokenList = lexer.tokenList
tokenList.append("$ $")  # todo verify if this needs to be done or not
tokenIndex = -1
currToken = ''


def nextToken():
    global tokenIndex, currToken
    tokenIndex = tokenIndex + 1
    try:
        tokenString = tokenList[tokenIndex]
        currToken = tokenString.split(" ")
    except IndexError:
        currToken[0] = '$'
        currToken[1] = '$'  # Should not call the method. The grammar should be accepted on the last "$"


def previousToken():
    global tokenIndex, currToken
    tokenIndex = tokenIndex - 1
    try:
        tokenString = tokenList[tokenIndex]
        currToken = tokenString.split(" ")
    except IndexError:
        tokenString = tokenList[0]
        currToken = tokenString.split(" ")  # Should not call the method. The grammar should be accepted on the last "$"


def start():
    if program():
        nextToken()
        if currToken[1] == '$':
            print("ACCEPT")
            return
    print("REJECT")


def program():
    return declarationList()


def declarationList():
    nextToken()  # first token
    if currToken[0] == "Keyword":
        if (currToken[1] == "int" or currToken[1] == "void"):
            if (declaration()):
                if (fixedDecList()):
                    return True
    return False


def fixedDecList():
    nextToken()
    if currToken[0] == "Keyword":
        if (currToken[1] == "int" or currToken[1] == "void"):
            if (declaration()):
                fixedDecList()
                return True
    elif currToken[0] == "$":
        return True
    return False
    # empty state todo DO I need to look into follow sets?


def declaration():
    nextToken()
    if (currToken[0] == 'ID'):
        nextToken()
        if (currToken[0] == '('):  # goes to params() if ( exist
            if params():
                nextToken()
                if (currToken[0] == ')'):
                    compoundStmt()
                    return True
    return False


def varDeclaration():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "int" or currToken[1] == "void":
            nextToken()
            if currToken[0] == "ID":
                nextToken()
                if currToken[0] == "[":
                    nextToken()
                    if currToken[0] == "NUM":
                        nextToken()
                        if currToken[0] == "]":
                            nextToken()
                            if currToken[0] == ";":
                                return True
                elif currToken[0] == ";":
                    return True
    return False


def params():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "void":
            nextToken()
            if currToken[0] == "ID":
                nextToken()
                if currToken[0] == "[":
                    if currToken[0] == "]":
                        return True
                elif currToken[0] == ")" or currToken[1] == ",":
                    previousToken()
                    fixedParList()
            elif currToken[0] == ")":
                previousToken()
                return True
    return False


start()
