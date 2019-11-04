# Assume the test file is lexically correct
import lexer, copy

tokenList = lexer.tokenList
tokenList.append("$ $")  # todo verify if this needs to be done or not
tokenIndex = -1
currToken = ''

stack = []  # use list as a stack
# stack[0] will be the gloabal symbol table and would be copied to each table in the list
# for global variables
stack.append({})
currentStackIndex = 0
FST = {}  #to keep track of the functions

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
            if 'main' in stack[0]:
                if stack[0]['main'][0] == 'func':
                    print("ACCEPT")
                    exit(0)
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
                    varMeta = varDeclaration()
                    stack[currentStackIndex][varMeta[1]] = varMeta
    return


def validDec(token):
    global stack, currentStackIndex
    if token in stack[currentStackIndex]:
        print("REJECT")
        exit(0)
    if token in stack[0]:
        if stack[0][token][0] == "func":
            print("REJECT")
            exit(0)


def varDeclaration():
    nextToken()
    retList = []
    if currToken[0] == "Keyword":
        if currToken[1] == "void":
            print("REJECT")
            exit(0)
        if currToken[1] == "int":
            retList.append(currToken[1])
            nextToken()
            if currToken[0] == "ID":
                validDec(currToken[1])
                retList.append(currToken[1])
                nextToken()
                if currToken[0] == "[":
                    nextToken()
                    retList.append("arr")  #if array
                    if currToken[0] == "Num":
                        retList.append(currToken[1])
                        nextToken()
                        if currToken[0] == "]":
                            nextToken()
                            if currToken[0] == ";":
                                return retList
                elif currToken[0] == ";":
                    return retList
    return retList


def funDeclaration():
    nextToken()
    global stack, currentStackIndex, FST
    retList = []  #type specifier, id, params, return type
    retList.append("func")
    if currToken[0] == "Keyword":
        if currToken[1] == "int" or currToken[1] == "void":
            retList.append(currToken[1])
            nextToken()
            if currToken[0] == "ID":
                if currToken[1] in stack[currentStackIndex] or currToken[1] in stack[0]:
                    print("REJECT")
                    exit(0)
                # todo validFunc
                retList.append(currToken[1])
                nextToken()
                if currToken[0] == "(":
                    # add the ST to the table and copy the globals
                    currentStackIndex += 1
                    stack.append(copy.deepcopy(stack[0]))
                    stack[currentStackIndex]['funcName'] = retList[2]
                    retList.append(params())
                    nextToken()
                    if currToken[0] == ")":
                        stack[0][retList[2]] = retList
                        compoundStmt()
                        stack.pop()
                        currentStackIndex -= 1
    print(stack)
    return


paramList = []
def params():
    global paramList
    paramList = []
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
                    return paramList
    return paramList


def param():
    tempList = []
    global paramList
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "int" or currToken[1] == "void":
            tempList.append(currToken[1])
            nextToken()
            if currToken[0] == "ID":
                validDec(currToken[1])
                tempList.append(currToken[1])
                nextToken()
                if currToken[0] == "[":
                    tempList.append("arr")
                    nextToken()
                    if currToken[0] == "]":
                        paramList.append(tempList)
                        stack[currentStackIndex][tempList[1]] = tempList
                elif currToken[0] == ")" or currToken[0] == ",":
                    previousToken()
                    paramList.append(tempList)
                    stack[currentStackIndex][tempList[1]] = tempList


def fixedParList():
    nextToken()
    if currToken[0] == ",":
        param()
        fixedParList()
    elif currToken[0] == ")":
        previousToken()
        return
    return


def compoundStmt():
    nextToken()
    if currToken[0] == "{":
        # print(stack)
        localDeclaration()
        statementList()
        nextToken()
        if currToken[0] == "}":
            # print(stack)
            return

    return


def localDeclaration():
    follow = ['(', ';', 'ID', 'Num', '{', 'Keyword', '}']
    Keywords = ['if', 'return', 'while']
    nextToken()
    if currToken[0] == "Keyword":
        if currToken[1] == "void" or currToken[1] == "int":
            previousToken()
            varMeta = varDeclaration()
            stack[currentStackIndex][varMeta[1]] = varMeta
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
    global stack, currentStackIndex
    if currToken[0] == "Keyword":
        if currToken[1] == "return":
            nextToken()
            if currToken[0] == ";":
                stack[currentStackIndex]['return'] = 'empty'
                ret = 'empty'
                stack[0][stack[currentStackIndex]['funcName']].append({"return": ret})
            elif currToken[0] == '(' or currToken[0] == 'ID' or currToken[0] == 'Num':
                #todo need to determine what is being returned and can check the function type too
                previousToken()
                expression()
                nextToken()
                stack[currentStackIndex]['return'] = 'something'
                ret = "something"
                stack[0][stack[currentStackIndex]['funcName']].append({"return": ret})
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
        if currToken[1] not in stack[currentStackIndex]:
            print("REJECT")
            exit(0)
        nextToken()
        if currToken[0] == "[":
            #todo check the number falls in the range initialized
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
        if currToken[1] not in stack[0]:
            print("REJECT")
            exit(0)
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
    expression()
    fixedArgList()
    return


def fixedArgList():
    nextToken()
    if currToken[0] == ",":
        expression()
        fixedArgList()
    elif currToken[0] == ')':
        previousToken()
        return
    return


start()
