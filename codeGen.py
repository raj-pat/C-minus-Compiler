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
    if currToken[1] == '$':
        if 'main' in stack[0]:
            if stack[0]['main'][0] == 'func':
                print("ACCEPT")
                return

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
                    # print(codeline)
                    stack[currentStackIndex][varMeta[1]] = varMeta

    return


def varDeclaration():
    nextToken()
    retList = []
    if currToken[0] == "Keyword":

        if currToken[1] == "int":
            retList.append(currToken[1])
            nextToken()
            if currToken[0] == "ID":


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
    codeline2 = [''] * 4
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
                codeline2[3] = currToken[1]
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

    codeline2[0] = "end"
    codeline2[1] = "func"
    codegen.append(codeline2)
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
    relop = {'!=': "jneq", '<': "jlt", '<=': "jlte", '==': "jeq", '>': 'jgt', '>=': 'jgte'}
    global codegen, currTemp

    jmpLine = [""] * 4
    relOpLine = [""] * 4
    jmpLine[0] = "jmp"
    if currToken[0] == "Keyword":
        if currToken[1] == "if":
            nextToken()
            if currToken[0] == "(":
                retExp = expression()
                if retExp[0] == None:
                    genTemp()
                    codegen.append(["comp", 0, retExp[1], currTemp])
                    codegen.append(["jlt", currTemp, "", len(codegen) + 2])
                    codegen.append(jmpLine)
                else:
                    codegen.append([relop[retExp[0]], retExp[1], "", len(codegen) + 2])
                    codegen.append(jmpLine)
                nextToken()
                if currToken[0] == ")":
                    statement()
                    jmpElse = [''] * 4
                    jmpElse[0] = 'jmp'
                    codegen.append(jmpElse)
                    elsePart = fixedSelStmt()
                    if elsePart == None:
                        jmpLine[3] = len(codegen)

                    else:
                        jmpLine[3] = elsePart
                    jmpElse[3] = len(codegen)
    return


def fixedSelStmt():
    follow = ['(', ';', 'ID', 'Num', 'Keyword', '{', '}']
    Keywords = ['if', 'return', 'while']
    nextToken()
    ret = None
    if currToken[0] == "Keyword":
        if currToken[1] == "else":
            ret = len(codegen)
            statement()
        elif currToken[1] in Keywords:
            previousToken()

    elif currToken[0] in follow:
        if currToken[0] == "Keyword":
            if currToken[1] not in Keywords:
                return None
        previousToken()
        return None
    return ret


def iterationStmt():
    nextToken()
    global codegen, currTemp
    relop = {'!=': "jneq", '<': "jlt", '<=': "jlte", '==': "jeq", '>': 'jgt', '>=': 'jgte'}
    jmpLine = [''] * 4
    goUpLine = [''] * 4
    goUpLine[0] = 'jmp'
    goUpLine[3] = len(codegen)
    jmpLine[0] = 'jmp'
    if currToken[0] == "Keyword":
        if currToken[1] == "while":
            nextToken()
            if currToken[0] == "(":
                retExp = expression()
                if retExp[0] == None:
                    genTemp()
                    codegen.append(["comp", 0, retExp[1], currTemp])
                    codegen.append(["jlt", currTemp, "", len(codegen) + 2])
                    codegen.append(jmpLine)
                else:
                    codegen.append([relop[retExp[0]], retExp[1], "", len(codegen) + 2])
                    codegen.append(jmpLine)

                nextToken()
                if currToken[0] == ")":
                    statement()
                    codegen.append(goUpLine)
    jmpLine[3] = len(codegen)
    return


returnInvoked = False
def returnStmt():
    nextToken()
    global returnInvoked
    returnInvoked = True
    global stack, currentStackIndex, codegen, currTemp
    codeline = [""] * 4
    if currToken[0] == "Keyword":
        if currToken[1] == "return":
            codeline[0] = "return"
            nextToken()
            if currToken[0] == ";":
                codegen.append(codeline)
            elif currToken[0] == '(' or currToken[0] == 'ID' or currToken[0] == 'Num':
                previousToken()
                retType = expression()
                codeline[3] = retType[1]
                codegen.append(codeline)
                nextToken()
                if currToken[0] == ";":
                    return


def expression():
    follow = ['!=', ')', '*', '+', ',', '-', '/', ';', '<', '<=', '==', '>', '>=', ']']
    global codegen, currTemp
    codeline = [""] * 4
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
                codeline[0] = "assign"
                codeline[3] = ret
                retExp = expression()  # todo add below the return
                codeline[1] = retExp[1]
                codegen.append(codeline)
                return ret
            elif currToken[0] in follow:  # follow of Factor()
                previousToken()
                retFix = fixedTerm(ret)
                if retFix == None:
                    retFix = ret
                retAdd = fixedAddExp(retFix)
                if retAdd == None:
                    retAdd = retFix
                retOp = fixedSimExpr(retAdd)
                return retOp
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
                    codeline[2] = "todo"  #todo here
                    genTemp()
                    codeline[3] = currTemp
                    codegen.append(codeline)
                    # print(codeline)
                    retId = currTemp
                    retExp = expression()
                    try:
                        codeline[2] = int(retExp[1]) * 4
                    except:
                        codeline2 = [""] * 4
                        codeline2[0] = "mul"
                        codeline2[1] = retExp[1]
                    nextToken()
                    if currToken[0] == "]":
                        None
                return retId
        except IndexError:
            if currToken[0] in follow:
                previousToken()
                return retId

def simpleExpression():
    ret = additiveExpression()
    ret1 = fixedSimExpr(ret)
    return ret1


def fixedSimExpr(ls):
    global codegen, currTemp
    codeline = [""] * 4
    codeline[0] = "comp"
    codeline[1] = ls
    relop = ['!=', '<', '<=', '==', '>', '>=']
    nextToken()
    rel = ""
    if currToken[0] in relop:
        rel = currToken[0]
        ret = additiveExpression()
        codeline[2] = ret
        genTemp()
        codeline[3] = currTemp
        codegen.append(codeline)
    elif currToken[0] == ')' or currToken[0] == ',' or currToken[0] == ';' or currToken[0] == ']':
        previousToken()
        return [None, ls]
    return [rel, currTemp]


def additiveExpression():
    ret = term()
    retFix = fixedAddExp(ret)
    if retFix == None:
        return ret
    else:
        return retFix



def fixedAddExp(ls):
    follow = ['!=', ')', ',', ';', '<', '<=', '==', '>', '>=', ']']
    global codegen, currTemp
    codeline = [''] * 4
    nextToken()
    if currToken[0] == '+' or currToken[0] == '-':
        if currToken[0] == "+":
            codeline[0] = "add"
        else:
            codeline[0] = "sub"
        codeline[1] = ls
        ret = term()
        codeline[2] = ret
        genTemp()
        codeline[3] = currTemp
        codegen.append(codeline)
        fixedAddExp(currTemp)
    elif currToken[0] in follow:
        previousToken()
        return None
    return currTemp


def term():
    ret = factor()
    k = fixedTerm(ret)
    if k == None:
        # print("ret " + ret)
        return ret
    else:
        # print("ret " + k)
        return k



def fixedTerm(ls):
    follow = ['!=', ')', ',', ';', '<', '<=', '==', '>', '>=', ']', '+', '-']
    global codegen, currTemp
    codeline = [""] *4

    nextToken()
    if currToken[0] == "*" or currToken[0] == "/":
        if currToken[0] == '*':
            codeline[0] = "mul"
        else:
            codeline[0] = "div"
        ret = factor()
        codeline[1] = ls
        codeline[2] = ret
        genTemp()
        codeline[3] = currTemp

        codegen.append(codeline)
        fixedTerm(currTemp)
    elif currToken[0] in follow:
        previousToken()
        return None
    return currTemp


def factor():
    # follow = ['!=' ,')' ,',' ,';' ,'<' ,'<=' ,'==' ,'>','>=', ']', '+', '-','*','/','=']
    nextToken()
    if currToken[0] == "(":
        ret = expression()  # todo make sure expression returns something
        nextToken()
        if currToken[0] == ")":
            return ret[1]
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
    global argListVar, codegen, currTemp
    codeline = [""] * 4
    codegen.append(codeline)

    codeline[0] = "call"
    argListVar = []
    retType = ""
    nextToken()
    if currToken[0] == "ID":
        codeline[1] = currToken[1]

        funMeta = stack[0][currToken[1]]
        retType = funMeta[1]
        nextToken()
        if currToken[0] == "(":
            args()
            nextToken()
            if currToken[0] == ")":
                None
        codeline[2] = len(argListVar)
        genTemp()
        codeline[3] = currTemp

    return currTemp


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
i = 0
# print("{: >20} {: >20} {: >20}".format(*row))
for lis in codegen:
    print(str(i) + " " * (5 - len(str(i))), end="")
    print(str(lis[0]) + " " * (12 - len(str(lis[0]))), end="")
    print(str(lis[1]) + " " * (12 - len(str(lis[1]))), end="")
    print(str(lis[2]) + " " * (12 - len(str(lis[2]))), end="")
    print(str(lis[3]) + " " * (12 - len(str(lis[3]))))
    i += 1
