# This project file will read the input and would return the token information tp parser file.
# #pseudo code
# for each word
#     if word has valid chars
#         for each letter
#             if comment is off
#                 concatenate if the letter is [a-zA-Z] or [0-9]
#             else
#                     if letter is a space or any valid character
#                         check the concatenated var
#                         if it is a letter or a num
#                                 if keyword or id or num and return
#                             return the value of the key of the current char if its not space and is valid
#
#                     if letter is [0-9]
#                         maybe an error or not -> check the grammar
#         #when the word ends
#         check the concatenate word and determine if it's an id or a keyword or a num
#     else
#     return error for invalid symbol.



def lexer(filename):
    inputFile = open(filename, 'r')
    keywords = ['else', 'if', 'int', 'return', 'void', 'while']
    validChars = {'(': '(', ')': ')', '{': '{', '}': '}', '[': '[', ']': ']', ';': ';', '*': 'mulop', '/': 'mulop',
                  '+': 'addop', '-': 'addop', '<': 'relop', '<=': 'relop', '>': 'relop', '>=': 'relop', '==': 'relop',
                  '!=': 'relop', '=': '=', '\,': '\,', '/*', '*/'}
    for line in inputFile:
        words = line.split()
        print("Input: " + line)
        for word in words:
            if word in keywords:
                print('Keyword: ' + word)





lexer('test')
