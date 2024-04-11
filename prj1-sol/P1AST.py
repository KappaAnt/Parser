#!/usr/bin/env python3

import re
import sys
from collections import namedtuple
import json

"""
TOP DOWN: Write Start Symbols to Terminals

New Grammar Needed to produce AST: Abstract Syntax Tree

I think this is it
program
  : declaration*
  ;
declaration
  : declarationSpecifier struct '=' identifier ';'
  | #empty
  ;
declarationSpecifier
  : 'const'
  | 'let'
  ;
struct
  : identifier
  | arrayStruct
  | objectStruct
  ;
arrayStruct
  : '[' (struct',')* struct ']'
  ;
objectStruct
  : '{' (keyStruct',')* keyStruct '}'
  ;
keyStruct
  : identifier (':' struct)?
  ;
identifier
  : [a-zA-Z|\_]+[a-zA-Z0-9|\_]*
  ;
_____________________________________

"""
def reservedError():
    print(f"expecting 'ID' but got 'RESERVED'",
                  file=sys.stderr)
    sys.exit(1)

def extraCommaError():
    print(f"expecting 'struct/keyStruct' but got ','",
                  file=sys.stderr)
    sys.exit(1)

def noCommaError():
    print(f"expecting ',' but got 'struct/keyStruct'",
                  file=sys.stderr)
    sys.exit(1)

def parse(text):

    #lookahead is type Token
    #lookahead is first assigned = nextToken()
    #Token is Token = namedtuple('Token', ['kind', 'lexeme'])

    #def Ast(keyWord, *struct, id):
    #struct_list = list(struct)
    #return {'decl': keyWord, 'struct': struct_list, 'id': id}
    #Our Dictionary ^^^

    def peek(kind): return lookahead.kind == kind
    def consume(kind):
        nonlocal lookahead
        if (lookahead.kind == kind):
            lookahead = nextToken()
        else:
            print(f"expecting '{kind}' but got '{lookahead.lexeme}'",
                  file=sys.stderr)
            sys.exit(1)
    def nextToken():
        nonlocal index
        if (index >= len(tokens)):
            return Token('EOF', '<EOF>')
        else:
            tok = tokens[index]
            index += 1
            return tok

    def program():
        asts = [] # We are going to append dictionary information to this list
        while (not peek('EOF')):
            asts.append(declaration()) #Specifically Ast dictionary info
            consume(';')    
        return asts

    def declaration():
        if(declarationSpecifier()):
            #We want our decl : keyWord
            keyWord = lookahead.lexeme # lookahead.lexeme is either 'const' or 'let'
            #Move onto next token and consume
            consume('Key')
            #Now deal with struct in grammar
            structObject = struct()
            #Move onto next token and consume
            consume('=')
            if(peek('ID')): #Consumes and creates ID string
                idString = identifier()
            else:
                reservedError()
            return Ast(keyWord, structObject, idString) #To append to ast list
            # ^^^ Ast dictionary object created

        else: #No keyword to start, no way
            return 

    def declarationSpecifier():
        return peek('Key')

    def struct():
        #struct can be an identifier | arrayStruct | objectStruct 
        if(peek('[')): #for arrayStruct we want 'struct' : list(struct)
            return arrayStruct()
        elif(peek('{')): #for objectStruct we want 'struct' : list(struct)
            return objectStruct()
        else: #for identifer we just want 'struct': id
            return identifier()

    def arrayStruct():
        #consume and advance to next token
        consume('[')
        listArrayStruct = []
        commaCounter = 0
        insertCounter = 0
        #star kleene closure for struct followed by , if there is another struct
        while(True):
            #Process one struct
            #This is tricky
            listArrayStruct.append(struct())
            insertCounter+=1
            if(peek(',')): # go again
                commaCounter+=1
                consume(',')
                if(peek(']')):
                    extraCommaError()
            else: # dont go again
                break
        if(commaCounter >= 0):
            if(insertCounter != (commaCounter +1)):
                noCommaError()
        consume(']')
        return listArrayStruct #return a list

    def objectStruct():
        #consume and advance to next token
        consume('{')
        dictionaryObjectStruct = {}
        commaCounter = 0
        insertCounter = 0
        while(True):
            # add to dictionaryObjectStruct
            myTuple = keyStruct()
            dictionaryObjectStruct[myTuple[0]] = myTuple[1]
            insertCounter+=1
            if(peek(',')): # go again
                commaCounter+=1
                consume(',')
                if(peek('}')):
                    extraCommaError()
            else: # dont go again
                break
        if(commaCounter >= 0):
            if(insertCounter != (commaCounter +1)):
                noCommaError()
        consume('}')
        return dictionaryObjectStruct

    def keyStruct():
        if(peek('ID')):
            idString = identifier()
        #The following is optional
        if(peek(':')): 
            consume(':') # Now another struct should be after this
            return (idString, struct())


        return (idString, idString)#We want to return a (key, value-member)

    def identifier():
        idTotal = ''
        #while(peek('ID')):
            #idTotal += lookahead.lexeme
            #consume('ID')        
        idTotal = lookahead.lexeme
        consume('ID')
        return idTotal #return a string

    #begin parse()
    #print('Before Scan:')
    tokens = scan(text)
    #print('After Scan:')
    index = 0
    lookahead = nextToken()
    value = program()
    if (not peek('EOF')):
        print(f'expecting <EOF>, got {lookahead.lexeme}', file=sys.stderr)
        sys.exit(1)
    return value #Returning the AST list from declaration()

def scan(text):
    #If im correct, the order of these can be verified in parsing after the scan

    SPACE_RE = re.compile(r'\s+|\/\/.*') #Ignore WhiteSpace and Comments
    NEWLINE_RE = re.compile(r'\n') #Ignore newLine
    KEY_RE = re.compile(r'\b(const|let)\b') #KeyWords
    BRACK_RE = re.compile(r'[\[\]\{\}]') #Brackets
    COMMA_RE = re.compile(r',')
    COLON_RE = re.compile(r':')
    EQUAL_RE = re.compile(r'=')
    ID_RE = re.compile(r'[a-zA-Z|\_]+[a-zA-Z0-9|\_]*') #Identifiers
    SEMI_RE = re.compile(r';') #SemiColon
    def next_match(text): #python re.match module returns a match object
        #If we match at any specific regex with stated, we want to deal with that
        m = SPACE_RE.match(text) 
        if (m): return (m, None) #Ignore WhiteSpace and Comments with None, Deliberatly ignore whitespace and comments
        m = KEY_RE.match(text) 
        if (m): return (m, 'Key') #const/let
        m = BRACK_RE.match(text)
        if (m): return (m, m.group()) #brackets/squiggly
        m = COMMA_RE.match(text)  
        if (m): return (m, m.group()) # ,
        m = COLON_RE.match(text)  
        if (m): return (m, m.group()) # :
        m = EQUAL_RE.match(text)
        if (m): return (m, m.group()) # =
        m = ID_RE.match(text)  
        if (m): return (m, 'ID') #alphanumeric_
        m = SEMI_RE.match(text)  
        if (m): return (m, m.group()) # ;
        m = NEWLINE_RE.match(text) 
        if (m): return (m, None) #Ignore \n

    tokens = []
    while (len(text) > 0):
        (match, kind) = next_match(text)
        lexeme = match.group()
        if (kind): tokens.append(Token(kind, lexeme))
        text = text[len(lexeme):]
    
    #print(tokens)
    return tokens
#Scan Function ^


def readInput():
    #We want to read from standard input
    contents = ''
    for line in sys.stdin:
        contents = contents + line
    return contents

def main():
    contents = readInput()
    try:
        asts = parse(contents)
    #print ('After Final Parse on AST')
        print(json.dumps(asts, separators=(',', ':')))
    except Exception as e:
        print("ERROR : Is your input scannable?", file=sys.stderr)
        sys.exit(1)
    #finally:
    #print("\nFinished")
    

def readFile(path):
    with open(path, 'r') as file:
        content = file.read()
    return content


def usage():
    print(f'usage: {sys.argv[0]} DATA_FILE')
    sys.exit(1)

#use a dict so that we can add attributes dynamically
#def Ast(tag, *kids): ## * kids is not a pointer, it is a variable to unpack a kleen closure amount of arguments
    #return { 'tag': tag, 'xkids': kids }

def Ast(keyWord, struct, idString):
    struct_list = struct
    return {'decl': keyWord, 'struct': struct_list, 'id': idString}

Token = namedtuple('Token', ['kind', 'lexeme'])

if __name__ == "__main__":
    main()
