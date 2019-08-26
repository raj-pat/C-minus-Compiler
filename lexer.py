# This project file will read the input and would return the token information tp parser file.

def lexer(filename):
    inputFile = open(filename, 'r')
    for line in inputFile:
        print((line.strip()))


lexer('test')
