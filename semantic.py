# Assume the test file is lexically correct
import lexer

tokenList = lexer.tokenList
tokenList.append("$ $")  # todo verify if this needs to be done or not
tokenIndex = -1
currToken = ''

stack = []  # use list as a stack
mainST = {}  # for global variables
stack.append(mainST)
currentStackIndex = 0


# print(tokenList)

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
    program()
    nextToken()
    try:
        if currToken[1] == '$':
            print("ACCEPT")
            return
        print("REJECT")
    except IndexError:
        print("REJECT")


def program():
    declarationList()


def declarationList():
    declaration()
    fixedDecList()
    return


def fixedDecList():
    nextToken()
    if currToken[0] == "Keyword":
        if (currToken[1] == "int" or currToken[1] == "void"):
            previousToken()
            declaration()
            fixedDecList()
    elif currToken[0] == "$":
        previousToken()
        return
    return
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
                    funDeclaration()
                elif currToken[0] == ";" or currToken[0] == '[':
                    previousToken()
                    previousToken()
                    previousToken()
                    varDeclaration()
    return


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
                                return
                elif currToken[0] == ";":
                    return
    return


def funDeclaration():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "int" or currToken[1] == "void":
            nextToken()
            if currToken[0] == "ID":
                nextToken()
                if currToken[0] == "(":
                    params()
                    nextToken()
                    if currToken[0] == ")":
                        compoundStmt()
    return


def params():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "void" or currToken[1] == "int":
            nextToken()
            if currToken[0] == "ID":
                previousToken()
                previousToken()
                param()
                fixedParList()
            elif currToken[0] == ")":
                previousToken()
                if currToken[1] == "void":
                    return
    return


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
                        return
                elif currToken[0] == ")" or currToken[0] == ",":
                    previousToken()
                    return
    return


def fixedParList():
    nextToken()
    if currToken[0] == ",":
        if params():
            fixedParList()
    elif currToken[0] == ")":
        previousToken()
        return
    return


def compoundStmt():
    nextToken()
    if currToken[0] == "{":
        localDeclaration()
        statementList()
        nextToken()
        if currToken[0] == "}":
            return

    return


def localDeclaration():
    follow = ['(', ';', 'ID', 'Num', '{', 'Keyword', '}']
    Keywords = ['if', 'return', 'while']
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "void" or currToken[1] == "int":
            previousToken()
            varDeclaration()
            localDeclaration()
        elif currToken[1] == "return" or currToken[1] == "if" or currToken[1] == "while":
            previousToken()
            return
    elif currToken[0] in follow:
        if currToken[0] == "Keyword":
            if currToken[1] not in Keywords:  # todo check exception wif index[1] dne
                return
        previousToken()
        return
    return


def statementList():
    first = ['(', ';', 'ID', 'Num', 'Keyword', '{']
    Keywords = ['if', 'return', 'while']

    nextToken()
    if currToken[0] in first:
        if currToken[0] == "Keyword":  # todo check exception wif index[1] dne
            if currToken[1] not in Keywords:
                return
        previousToken()
        statement()
        statementList()
    elif currToken[0] == "}":
        previousToken()
        return
    return


def statement():
    nextToken()
    if currToken[0] == "(" or currToken[0] == ';' or currToken[0] == 'ID' or currToken[0] == "Num":
        previousToken()
        expressionStmt()
    elif currToken[0] == "{":
        previousToken()
        compoundStmt()
    elif currToken[0] == "Keyword":
        if currToken[1] == "if":
            previousToken()
            selectionStmt()
        elif currToken[1] == "while":
            previousToken()
            iterationStmt()
        elif currToken[1] == "return":
            previousToken()
            returnStmt()
    return


def expressionStmt():
    nextToken()
    if currToken[0] == '(' or currToken[0] == 'ID' or currToken[0] == 'Num':
        previousToken()
        expression()
        nextToken()
        if currToken[0] == ";":
            return
    elif currToken[0] == ";":
        return
    return


def selectionStmt():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "if":
            nextToken()
            if currToken[0] == "(":
                expression()
                    nextToken()
                    if currToken[0] == ")":
                        statement()
                        fixedSelStmt()
    return


def fixedSelStmt():
    follow = ['(', ';', 'ID', 'Num', 'Keyword', '{', '}']
    Keywords = ['if', 'return', 'while']
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "else":
            statement()
        elif currToken[1] in Keywords:
            previousToken()
            return
    elif currToken[0] in follow:
        if currToken[0] == "Keyword":
            if currToken[1] not in Keywords:
                return
        previousToken()
        return
    return


def iterationStmt():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "while":
            nextToken()
            if currToken[0] == "(":
                expression()
                nextToken()
                if currToken[0] == ")":
                    statement()
    return


def returnStmt():
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "return":
            nextToken()
            if currToken[0] == ";":
                return
            elif currToken[0] == '(' or currToken[0] == 'ID' or currToken[0] == 'Num':
                previousToken()
                expression()
                nextToken()
                if currToken[0] == ";":
                    return


def expression():
    follow = ['!=', ')', '*', '+', ',', '-', '/', ';', '<', '<=', '==', '>', '>=', ']']
    nextToken()
    if currToken[0] == "ID":
        nextToken()
        if currToken[0] == "=" or currToken[0] == "[":
            previousToken()
            previousToken()
            var()
            nextToken()
            if currToken[0] == "=":
                expression()
            elif currToken[0] in follow:  # follow of Factor()
                previousToken()
                fixedTerm()
                fixedAddExp()
                fixedSimExpr()
        else:
            previousToken()
            previousToken()
            simpleExpression()
    elif currToken[0] == '(' or currToken[0] == 'Num':
        previousToken()
        simpleExpression()
    return


def var():
    follow = ['!=', ')', '*', '+', ',', '-', '/', ';', '<', '<=', '=', '==', '>', '>=', ']']
    nextToken()
    if currToken[0] == "ID":
        nextToken()
        if currToken[0] == "[":
            expression()
            nextToken()
            if currToken[0] == "]":
                return
        elif currToken[0] in follow:
            previousToken()
            return
    return


def simpleExpression():
    additiveExpression()
    fixedSimExpr()
    return


def fixedSimExpr():
    relop = ['!=', '<', '<=', '==', '>', '>=']
    nextToken()
    if currToken[0] in relop:
        additiveExpression()
    elif currToken[0] == ')' or currToken[0] == ',' or currToken[0] == ';' or currToken[0] == ']':
        previousToken()
        return
    return


def additiveExpression():
    term()
    fixedAddExp()
    return


def fixedAddExp():
    follow = ['!=', ')', ',', ';', '<', '<=', '==', '>', '>=', ']']
    nextToken()
    if currToken[0] == '+' or currToken[0] == '-':
        term()
        fixedAddExp()
    elif currToken[0] in follow:
        previousToken()
        return
    return


def term():
    factor()
    fixedTerm()


def fixedTerm():
    follow = ['!=', ')', ',', ';', '<', '<=', '==', '>', '>=', ']', '+', '-']
    nextToken()
    if currToken[0] == "*" or currToken[0] == "/":
        factor()
        fixedTerm()
    elif currToken[0] in follow:
        previousToken()
        return
    return


def factor():
    # follow = ['!=' ,')' ,',' ,';' ,'<' ,'<=' ,'==' ,'>','>=', ']', '+', '-','*','/','=']
    nextToken()
    if currToken[0] == "(":
        expression()
        nextToken()
        if currToken[0] == ")":
            return
    elif currToken[0] == "ID":
        nextToken()
        if currToken[0] == "(":
            previousToken()
            previousToken()
            call()
        else:
            previousToken()
            previousToken()
            var()
    elif currToken[0] == "Num":
        return
    return


def call():
    nextToken()
    if currToken[0] == "ID":
        nextToken()
        if currToken[0] == "(":
            args()
            nextToken()
            if currToken[0] == ")":
                return
    return


def args():
    nextToken()
    if currToken[0] == '(' or currToken[0] == 'ID' or currToken[0] == 'Num':
        previousToken()
        argList()
    elif currToken[0] == ')':
        previousToken()
        return
    return


def argList():
    if expression():
        return fixedArgList()
    return


def fixedArgList():
    nextToken()
    if currToken[0] == ",":
        if expression():
            fixedArgList()
    elif currToken[0] == ')':
        previousToken()
        return
    return


start()
