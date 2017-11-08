# -*- coding: utf-8 -*-

from enum import Enum

class TokenClass(Enum):
    ID = 1
    NUMCONST = 2
    CHARCONST = 3
    KEYWORD = 4
    OPERATOR = 5
    SEPARATOR = 6

    def __str__(self):
        return self.name

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
        return "Token '{}' with value '{}' in line: {}, col: {}".format(self.token_class,
            self.value, self.line, self.column)

    def __repr__(self):
        return "Token class: {}, Value: {}".format(self.token_class, self.value)

class PatternHelpers():
    
    def is_blank(self, char):
        blanks = [" ", "\t", "\n"]
        return char in blanks

    def is_separator(self, char):
        separators = [".", ",", ";", "(", ")", "{", "}", "[", "]"]
        return char in separators

    def is_operator(self, char):
        #TODO: add 'and', 'or' and 'not'
        operators = ["+", "-", "*", "/", "%", "?", ">", "<", "=", ">=", "<=",
                     "==", "!", "+=", "-=", "*=", "/=", "++", "--"]
        return char in operators

    def is_comment(self, line, read_pos):
        return line[read_pos] == '/' and read_pos + 1 < len(line) and line[read_pos + 1] == '/'

    def is_keyword(self, lexeme):
        keywords = ["int","record","static", "bool", "char", "if",
                     "else", "while", "return", "break", "true", "false"]
        return lexeme in keywords

class SymbolTable():
    def __init__(self):
        self.hashtable = {}
    
    def store(self, token):
        if token.value not in self.hashtable:
            self.hashtable[token.value] = token
    
    def lookup(self, value):
        if self.hashtable[value]:
            return self.hashtable[value]
        return None