# -*- coding: utf-8 -*-

from enum import Enum

class TokenClass(Enum):
    ID = 1
    NUMCONST = 2
    CHARCONST = 3
    KEYWORD = 4
    OPERATOR = 5
    SEPARATOR = 6

    @classmethod
    def validate(classes, value):
        if isinstance(value, int):
            if (any(value == id.value for id in classes)):
                return

        if isinstance(value, str):
            if value in TokenClass.__members__:
                return
        
        if issubclass(type(value), Enum):
            return

        raise Exception("Token class identifier is not valid: '{}'".format(value))

class Token():
    def __init__(self, token_class, value, line, column):
        TokenClass.validate(token_class)

        self.token_class = token_class
        self.line = line + 1
        self.column = column + 1
        self.value = value
    
    def __str__(self):
        return "{} in line: {}, col: {}".format(self.value, self.line, self.column)

    def __repr__(self):
        return "Token class: {}, Value: {}".format(self.token_class, self.value)


class Scanner():
    def __init__(self, source_code):
        if len(source_code) == 0:
            raise Exception("Source code file is empty")
        self.code = source_code
        self.tokens = []

    def read_numconst(self, position, line):
        value = ""
        while position < len(line) and line[position].isdigit():
            value += line[position]
            position += 1
        return value, position

    def scan(self):
        line_pos = 0
        for line in self.code:
            read_pos = 0
            while read_pos < len(line):
                if line[read_pos].isdigit():
                    token_value, read_pos = self.read_numconst(read_pos, line)
                    token = Token(TokenClass.NUMCONST, token_value, line_pos, read_pos)
                    self.tokens.append(token)
            
            line_pos += 1
        print(self.tokens)
