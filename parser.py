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


# def declarationList():
#     nextToken()  # first token
#     if currToken[0] == "Keyword":
#         if (currToken[1] == "int" or currToken[1] == "void"):
#             if (declaration()):
#                 if (fixedDecList()):
#                     return True
#     return False
def declarationList():
    if declaration():
        return fixedDecList()
    return False



def fixedDecList():
    nextToken()
    if currToken[0] == "Keyword":
        if (currToken[1] == "int" or currToken[1] == "void"):
            previousToken()
            if (declaration()):
                return fixedDecList()
    elif currToken[0] == "$":
        previousToken()
        return True
    return False
    # empty state todo DO I need to look into follow sets?


def declaration():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "int" or currToken[1] == "void":
            nextToken()
            if (currToken[0] == 'ID'):
                nextToken()
                if (currToken[0] == '('):  # goes to params() if ( exist
                    previousToken()
                    previousToken()
                    previousToken()
                    return funDeclaration()
                elif currToken[0] == ";":
                    previousToken()
                    previousToken()
                    previousToken()
                    return varDeclaration()
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
                    if currToken[0] == "Num":
                        nextToken()
                        if currToken[0] == "]":
                            nextToken()
                            if currToken[0] == ";":
                                return True
                elif currToken[0] == ";":
                    return True
    return False


def funDeclaration():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "int" or currToken[1] == "void":
            nextToken()
            if currToken[0] == "ID":
                nextToken()
                if currToken[0] == "(":
                    if params():
                        nextToken()
                        if currToken[0] == ")":
                            return compoundStmt()
    return False


def params():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "void" or currToken[1] == "int":
            nextToken()
            if currToken[0] == "ID":
                previousToken()
                previousToken()
                if param():
                    return fixedParList()
            elif currToken[0] == ")":
                previousToken()
                if currToken[1] == "void":
                    return True
    return False





def param():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "int" or currToken[1] == "void":
            nextToken()
            if currToken[0] == "ID":
                nextToken()
                if currToken[0] == "[":
                    nextToken()
                    if currToken[0] == "]":
                        return True
                elif currToken[0] == ")" or currToken[0] == ",":
                    previousToken()
                    return True
    return False


def fixedParList():
    nextToken()
    if currToken[0] == ",":
        if params():
            return fixedParList()
    elif currToken[0] == ")":
        previousToken()
        return True
    return False


def compoundStmt():
    nextToken()
    if currToken[0] == "{":
        if localDeclaration():
            if statementList():
                nextToken()
                if currToken[0] == "}":
                    return True
    return False


def localDeclaration():
    follow = ['(', ';', 'ID', 'Num', '{', 'Keyword', '}']
    Keywords = ['if', 'return', 'while']
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "void" or currToken[1] == "int":
            previousToken()
            if varDeclaration():
                return localDeclaration()
        elif currToken[1] == "return" or currToken[1] == "if" or currToken[1] == "while":
            previousToken()
            return True
    elif currToken[0] in follow:
        if currToken[0] == "Keyword":
            if currToken[1] not in Keywords:  # todo check exception wif index[1] dne
                return False
        previousToken()
        return True
    return False


def statementList():
    first = ['(', ';', 'ID', 'Num', 'Keyword', '{']
    Keywords = ['if', 'return', 'while']

    nextToken()
    if currToken[0] in first:
        if currToken[0] == "Keyword":  # todo check exception wif index[1] dne
            if currToken[1] not in Keywords:
                return False
        previousToken()
        if statement():
            return statementList()
    elif currToken[0] == "}":
        previousToken()
        return True
    return False


def statement():
    nextToken()
    if currToken[0] == "(" or currToken[0] == ';' or currToken[0] == 'ID' or currToken[0] == "Num":
        previousToken()
        return expressionStmt()
    elif currToken[0] == "{":
        previousToken()
        return compoundStmt()
    elif currToken[0] == "Keyword":
        if currToken[1] == "if":
            previousToken()
            return selectionStmt()
        elif currToken[1] == "while":
            previousToken()
            return iterationStmt()
        elif currToken[1] == "return":
            previousToken()
            return returnStmt()
    return False


def expressionStmt():
    nextToken()
    if currToken[0] == '(' or currToken[0] == 'ID' or currToken[0] == 'Num':
        previousToken()
        if expression():
            nextToken()
            if currToken[0] == ";":
                return True
    elif currToken[0] == ";":
        return True
    return False


def selectionStmt():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "if":
            nextToken()
            if currToken[0] == "(":
                if expression():
                    nextToken()
                    if currToken[0] == ")":
                        if statement():
                            return fixedSelStmt()
    return False


def fixedSelStmt():
    follow = ['(', ';', 'ID', 'Num', 'Keyword', '{', '}']
    Keywords = ['if', 'return', 'while']
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "else":
            return statement()
    elif currToken[0] in follow:
        if currToken[0] == "Keyword":
            if currToken[1] not in Keywords:
                return False
        previousToken()
        return True
    return False


def iterationStmt():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "while":
            nextToken()
            if currToken[0] == "(":
                if expression():
                    nextToken()
                    if currToken[0] == ")":
                        return statement()
    return False


def returnStmt():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "return":
            nextToken()
            if currToken[0] == ";":
                return True
            elif currToken[0] == '(' or currToken[0] == 'ID' or currToken[0] == 'Num':
                previousToken()
                if expression():
                    nextToken()
                    if currToken[0] == ";":
                        return True


def expression():
    nextToken()
    if currToken[0] == "ID":
        nextToken()
        if currToken[0] == "=":
            previousToken()
            previousToken()
            if var():
                nextToken()
                if currToken[0] == "=":
                    return expression()
        else:
            previousToken()
            previousToken()
            return simpleExpression()
    elif currToken[0] == '(' or currToken[0] == 'Num':
        previousToken()
        return simpleExpression()
    return False


def var():
    follow = ['!=', ')', '*', '+', ',', '-', '/', ';', '<', '<=', '=', '==', '>', '>=', ']']
    nextToken()
    if currToken[0] == "ID":
        nextToken()
        if currToken[0] == "[":
            if expression():
                nextToken()
                if currToken[0] == "]":
                    return True
        elif currToken[0] in follow:
            previousToken()
            return True
    return False


def simpleExpression():
    if additiveExpression():
        return fixedSimExpr()
    return False


def fixedSimExpr():
    relop = ['!=', '<', '<=', '==', '>', '>=']
    nextToken()
    if currToken[0] in relop:
        return additiveExpression()
    elif currToken[0] == ')' or currToken[0] == ',' or currToken[0] == ';' or currToken[0] == ']':
        previousToken()
        return True
    return False


def additiveExpression():
    if term():
        return fixedAddExp()
    return False


def fixedAddExp():
    follow = ['!=', ')', ',', ';', '<', '<=', '==', '>', '>=', ']']
    nextToken()
    if currToken[0] == '+' or currToken[0] == '-':
        if term():
            return fixedAddExp()
    elif currToken[0] in follow:
        previousToken()
        return True
    return False


def term():
    if factor():
        return fixedTerm()


def fixedTerm():
    follow = ['!=', ')', ',', ';', '<', '<=', '==', '>', '>=', ']', '+', '-']
    nextToken()
    if currToken[0] == "*" or currToken[0] == "/":
        if factor():
            return fixedTerm()
    elif currToken[0] in follow:
        previousToken()
        return True
    return False


def factor():
    # follow = ['!=' ,')' ,',' ,';' ,'<' ,'<=' ,'==' ,'>','>=', ']', '+', '-','*','/','=']
    nextToken()
    if currToken[0] == "(":
        if expression():
            nextToken()
            if currToken[0] == ")":
                return True
    elif currToken[0] == "ID":
        nextToken()
        if currToken[0] == "(":
            previousToken()
            previousToken()
            return call()
        else:
            previousToken()
            previousToken()
            return var()
    elif currToken[0] == "Num":
        return True
    # elif currToken[0] in follow:
    #     previousToken()
    #     return True
    return False


def call():
    nextToken()
    if currToken[0] == "ID":
        nextToken()
        if currToken[0] == "(":
            if args():
                nextToken()
                if currToken[0] == ")":
                    return True
    return False


def args():
    nextToken()
    if currToken[0] == '(' or currToken[0] == 'ID' or currToken[0] == 'Num':
        previousToken()
        return argList()
    elif currToken[0] == ')':
        previousToken()
        return True
    return False


def argList():
    if expression():
        return fixedArgList()
    return False


def fixedArgList():
    nextToken()
    if currToken[0] == ",":
        if expression():
            return fixedArgList()
    elif currToken[0] == ')':
        previousToken()
        return True
    return False

start()
