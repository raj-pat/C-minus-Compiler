# Assume the test file is lexically correct
import lexer, copy

tokenList = lexer.tokenList
tokenList.append("$ $")  # todo verify if this needs to be done or not
tokenIndex = -1
currToken = ''

stack = []  # use list as a symbol table stack
# stack[0] will be the global symbol table and would be copied to each table in the list
# for global variables
stack.append({})
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
                    try:
                        if varMeta[2] == "arr":
                            for i in range(int(varMeta[3])):
                                stack[currentStackIndex][varMeta[1] + '[' + str(i) + ']'] = varMeta[:2]
                        stack[currentStackIndex][varMeta[1]] = [varMeta[0], 'arr']
                    except IndexError:
                        stack[currentStackIndex][varMeta[1]] = varMeta
    return


def validDec(token):
    global stack, currentStackIndex
    if token in stack[currentStackIndex]:
        try:
            if stack[currentStackIndex]['innerScope']:
                None
        except KeyError:
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
                                None
                elif currToken[0] == ";":
                    None
    return retList


funcStack = []
def funDeclaration():
    nextToken()
    global stack, currentStackIndex, FST, returnInvoked, funcStack
    returnInvoked = False
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
                    stack[currentStackIndex]['innerScope'] = False
                    stack[currentStackIndex]['funcName'] = retList[2]
                    retList.append(params())
                    funcStack.append(retList[2])
                    nextToken()
                    if currToken[0] == ")":
                        stack[0][retList[2]] = retList
                        compoundStmt(True)
                        stack.pop()
                        currentStackIndex -= 1
                        funcStack.pop()

    print(stack)
    if not returnInvoked:
        if retList[1] == "int":
            print("REJECT")
            exit(0)
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


def compoundStmt(newFunction=False):
    nextToken()
    global funcStack, currentStackIndex
    if not newFunction:  # for {} in a method
        stack.append(copy.deepcopy(stack[currentStackIndex]))
        stack[currentStackIndex]['funcName'] = funcStack[len(funcStack) - 1]
        stack[currentStackIndex]['innerScope'] = True
        currentStackIndex += 1

    if currToken[0] == "{":
        # print(stack)
        localDeclaration()
        statementList()
        nextToken()
        if currToken[0] == "}":
            if not newFunction:  # for {} in a method
                stack.pop()
                currentStackIndex -= 1
            return

    return


def localDeclaration():
    follow = ['(', ';', 'ID', 'Num', '{', 'Keyword', '}']
    Keywords = ['if', 'return', 'while']
    nextToken()
    if currToken[0] == "Keyword":  #todo no void variables
        if currToken[1] == "void" or currToken[1] == "int":
            previousToken()
            varMeta = varDeclaration()
            try:
                if varMeta[2] == "arr":
                    for i in range(int(varMeta[3])):
                        stack[currentStackIndex][varMeta[1] + '[' + str(i) + ']'] = varMeta[:2]
            except IndexError:
                stack[currentStackIndex][varMeta[1]] = varMeta
            localDeclaration()
        elif currToken[1] == "return" or currToken[1] == "if" or currToken[1] == "while":
            previousToken()
            return
    elif currToken[0] in follow:
        if currToken[0] == "Keyword":
            if currToken[1] not in Keywords:
                return
        previousToken()
        return
    return


def statementList():
    first = ['(', ';', 'ID', 'Num', 'Keyword', '{']
    Keywords = ['if', 'return', 'while']

    nextToken()
    if currToken[0] in first:
        if currToken[0] == "Keyword":
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
            returnStmt()  # verify the type returned
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


returnInvoked = False
def returnStmt():
    nextToken()
    global returnInvoked
    returnInvoked = True
    global stack, currentStackIndex
    if currToken[0] == "Keyword":
        if currToken[1] == "return":
            nextToken()
            if currToken[0] == ";":
                if stack[0][stack[currentStackIndex]['funcName']][1] != "void":
                    print("REJECT")
                    exit(0)
            elif currToken[0] == '(' or currToken[0] == 'ID' or currToken[0] == 'Num':

                previousToken()
                retType = expression()  # todo check if it is array rettype=['arr','True'] if returned is arr.
                if retType[0] != stack[0][stack[currentStackIndex]['funcName']][1] and retType[1] == True:
                    print("REJECT")
                    exit(0)
                nextToken()
                if currToken[0] == ";":
                    return


def expression():
    follow = ['!=', ')', '*', '+', ',', '-', '/', ';', '<', '<=', '==', '>', '>=', ']']
    nextToken()
    retExp = []
    ret = ""
    if currToken[0] == "ID":
        nextToken()
        if currToken[0] == "=" or currToken[0] == "[":
            previousToken()
            previousToken()
            ret = var()
            retExp.append(ret)
            nextToken()
            if currToken[0] == "=":
                if ret != expression()[0]:
                    print("REJECT")
                    exit(0)
            elif currToken[0] in follow:  # follow of Factor()
                previousToken()
                fixedTerm(ret)
                fixedAddExp(ret)
                if fixedSimExpr(ret) == "empty":
                    retExp.append(True)
                else:
                    retExp.append(False)
        else:
            previousToken()
            previousToken()
            retExp = simpleExpression()
            if retExp[1] == "empty":
                retExp[1] = True
            else:
                retExp[1] = False
    elif currToken[0] == '(' or currToken[0] == 'Num':
        previousToken()
        retExp = simpleExpression()
        if retExp[1] == "empty":
            retExp[1] = True
        else:
            retExp[1] = False
    return retExp


def var():
    follow = ['!=', ')', '*', '+', ',', '-', '/', ';', '<', '<=', '=', '==', '>', '>=', ']']
    nextToken()
    retType = ""
    if currToken[0] == "ID":
        if currToken[1] not in stack[currentStackIndex]:
            print("REJECT")
            exit(0)
        id = currToken[1]
        temp = stack[currentStackIndex][currToken[1]]

        nextToken()
        if temp[1] == 'arr':
            if currToken[0] == "[":
                # todo check the number falls in the range initialized
                nextToken()
                if currToken[0] == 'Num':
                    arr = id + '[' + currToken[1] + ']'
                    if not arr in stack[currentStackIndex]:
                        print("REJECT")
                        exit(0)
                else:
                    previousToken()
                    expression()
                nextToken()
                if currToken[0] == "]":
                    None
            retType = temp[0]
        elif currToken[0] in follow:
            previousToken()
            retType = temp[0]
    return retType


def simpleExpression():
    ret = additiveExpression()
    ret1 = fixedSimExpr(ret)
    return [ret, ret1]


def fixedSimExpr(ls):
    relop = ['!=', '<', '<=', '==', '>', '>=']
    nextToken()
    if currToken[0] in relop:
        ret = additiveExpression()
        if ret != ls:
            print("REJECT")
            exit(0)
        return ret
    elif currToken[0] == ')' or currToken[0] == ',' or currToken[0] == ';' or currToken[0] == ']':
        previousToken()
        return "empty"
    return "empty"


def additiveExpression():
    ret = term()
    fixedAddExp(ret)
    return ret


def fixedAddExp(ls):
    follow = ['!=', ')', ',', ';', '<', '<=', '==', '>', '>=', ']']
    nextToken()
    if currToken[0] == '+' or currToken[0] == '-':
        ret = term()
        if ls == ret:
            fixedAddExp(ret)
        else:
            print("REJECT")
            exit(0)
    elif currToken[0] in follow:
        previousToken()
        return
    return


def term():
    ret = factor()
    fixedTerm(ret)
    return ret


def fixedTerm(ls):
    follow = ['!=', ')', ',', ';', '<', '<=', '==', '>', '>=', ']', '+', '-']
    nextToken()
    if currToken[0] == "*" or currToken[0] == "/":
        ret = factor()
        if ret == ls:
            fixedTerm(ret)
        else:
            print("REJECT")
            exit(0)
    elif currToken[0] in follow:
        previousToken()
        return
    return


def factor():
    # follow = ['!=' ,')' ,',' ,';' ,'<' ,'<=' ,'==' ,'>','>=', ']', '+', '-','*','/','=']
    nextToken()
    if currToken[0] == "(":
        ret = expression()  # todo make sure expression returns something
        nextToken()
        if currToken[0] == ")":
            return ret
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
        return "int"
    return "error"


argListVar = []
def call():
    global argListVar
    argListVar = []
    retType = ""
    nextToken()
    if currToken[0] == "ID":
        if currToken[1] not in stack[0]:
            print("REJECT")
            exit(0)
        funMeta = stack[0][currToken[1]]
        retType = funMeta[1]
        nextToken()
        if currToken[0] == "(":
            args()
            nextToken()
            if currToken[0] == ")":
                None
        if len(funMeta[3]) != len(argListVar):
            print("REJECT")
            exit(0)
        for i in range(len(funMeta[3])):
            if funMeta[3][i][0] != argListVar[i][0]:
                print("REJECT")
                exit(0)

    return retType


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
    global argListVar
    argListVar.append(expression())
    fixedArgList()
    return


def fixedArgList():
    nextToken()
    if currToken[0] == ",":
        global argListVar
        argListVar.append(expression())
        fixedArgList()
    elif currToken[0] == ')':
        previousToken()
        return
    return


start()
