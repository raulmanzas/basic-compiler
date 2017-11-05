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