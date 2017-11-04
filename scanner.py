# -*- coding: utf-8 -*-

from enum import Enum

class TokenClass(Enum):
    ID = 1
    NUMCONST = 2
    CHARCONST = 3
    KEYWORD = 4
    OPERATOR = 5
    SEPARATOR = 6

class Token():
    def __init__(self, token_class, value, line, column):
        self.line = line
        self.column = column
        self.token_class = token_class
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
    
    def scan(self):
        print(self.code)