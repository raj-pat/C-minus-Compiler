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
codegen = []
tempNum = -1
currTemp = ""


def genTemp():
    global currTemp, tempNum
    tempNum += 1
    currTemp = "temp" + str(tempNum)

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
    global codegen
    codeline = [""] * 4
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
                    codeline[0] = "alloc"
                    try:
                        codeline[1] = int(varMeta[4]) * 4
                    except IndexError:
                        codeline[1] = 4
                    codeline[3] = varMeta[1]
                    codegen.append(codeline)
                    print(codeline)
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
                    retList.append("arr")  # if array
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
    global stack, currentStackIndex, FST, returnInvoked, funcStack, codegen
    codeline = [""] * 4
    codeline[0] = "func"
    codegen.append(codeline)
    nextToken()

    returnInvoked = False
    retList = []  # type specifier, id, params, return type
    retList.append("func")
    if currToken[0] == "Keyword":
        if currToken[1] == "int" or currToken[1] == "void":
            retList.append(currToken[1])
            nextToken()
            if currToken[0] == "ID":
                codeline[3] = currToken[1]
                if currToken[1] in stack[currentStackIndex] or currToken[1] in stack[0]:
                    print("REJECT")
                    exit(0)

                retList.append(currToken[1])
                nextToken()
                if currToken[0] == "(":
                    # add the ST to the table and copy the globals
                    currentStackIndex += 1
                    stack.append(copy.deepcopy(stack[0]))
                    stack[currentStackIndex]['innerScope'] = False
                    stack[currentStackIndex]['funcName'] = retList[2]
                    retParam = params()
                    retList.append(retParam)
                    codeline[1] = len(retParam)
                    for para in retParam:
                        codeline = [""] * 4
                        codeline[0] = "param"
                        codeline[3] = para[1]
                        codegen.append(codeline)
                    funcStack.append(retList[2])
                    nextToken()
                    if currToken[0] == ")":
                        stack[0][retList[2]] = retList
                        compoundStmt(True)
                        stack.pop()
                        currentStackIndex -= 1
                        funcStack.pop()
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
        if currToken[1] == "void":
            nextToken()
            if currToken[0] == ")":
                previousToken()
                if currToken[1] == "void":
                    return paramList
        elif currToken[1] == "int":
            nextToken()
            if currToken[0] == "ID":
                previousToken()
                previousToken()
                param()
                fixedParList()

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
    global codegen
    codeline = [""]*4
    follow = ['(', ';', 'ID', 'Num', '{', 'Keyword', '}']
    Keywords = ['if', 'return', 'while']
    nextToken()
    if currToken[0] == "Keyword":  #todo no void variables
        if currToken[1] == "void" or currToken[1] == "int":
            previousToken()
            varMeta = varDeclaration()
            print(varMeta)
            codeline[3] = varMeta[1]
            codeline[0] = "alloc"
            try:
                codeline[1] = int(varMeta[3]) * 4
            except IndexError:
                codeline[1] = 4
            codegen.append(codeline)

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
    ret = ""
    if currToken[0] == "ID":
        nextToken()
        if currToken[0] == "=" or currToken[0] == "[":
            previousToken()
            previousToken()
            ret = var()
            nextToken()
            if currToken[0] == "=":
                if ret != expression():
                    print("REJECT")
                    exit(0)
            elif currToken[0] in follow:  # follow of Factor()
                previousToken()
                fixedTerm(ret)
                fixedAddExp(ret)
        else:
            previousToken()
            previousToken()
            ret = simpleExpression()
    elif currToken[0] == '(' or currToken[0] == 'Num':
        previousToken()
        ret = simpleExpression()
    return ret


def var():
    global currTemp, codegen

    follow = ['!=', ')', '*', '+', ',', '-', '/', ';', '<', '<=', '=', '==', '>', '>=', ']']
    nextToken()
    retType = ""
    retId = ''
    if currToken[0] == "ID":

        if currToken[1] not in stack[currentStackIndex]:
            print("REJECT")
            exit(0)
        retId = currToken[1]
        temp = stack[currentStackIndex][currToken[1]]
        nextToken()
        try:
            if temp[2] == 'arr':
                if currToken[0] == "[":
                    # nextToken()
                    codeline = [""] * 4
                    codeline[0] = "disp"
                    codeline[1] = retId
                    codeline[2] = "todo"
                    genTemp()
                    codeline[3] = currTemp
                    codegen.append(codeline)
                    retId = currTemp
                    if expression() != "int":  # todo convert to a number somehow
                        print("REJECT")
                        exit(0)
                    nextToken()
                    if currToken[0] == "]":
                        None
                return retId
        except IndexError:
            if currToken[0] in follow:
                previousToken()
                return retId
            else:
                print("REJECT")
                exit(0)




def simpleExpression():
    ret = additiveExpression()
    ret1 = fixedSimExpr(ret)
    return ret


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
        if ls == ret and ls == 'int':
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
        return currToken[1]
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
            if funMeta[3][i][0] != argListVar[i]:
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
for lis in codegen:
    print(lis)
