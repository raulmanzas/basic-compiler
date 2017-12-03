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
        operators = ["+", "-", "*", "/", "%", "?", ">", "<", "=", ">=", "<=",
                     "==", "!", "+=", "-=", "*=", "/=", "++", "--"]
        return char in operators

    def is_logical_operator(self, lexeme):
        operators = ["and", "or", "not"]
        return lexeme in operators

    def is_comment(self, line, read_pos):
        return line[read_pos] == '/' and read_pos + 1 < len(line) and line[read_pos + 1] == '/'

    def is_keyword(self, lexeme):
        keywords = ["int","record","static", "bool", "char", "if",
                     "else", "while", "return", "break", "true", "false"]
        return lexeme in keywords

    def is_data_type(self, lexeme):
        types = ["int", "char", "bool"]
        return lexeme in types

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

    def __str__(self):
        representation = ""
        for key in self.hashtable.keys():
            representation += "Key: {} \n".format(key)
        
        return representation

class SyntaxNodeTypes(Enum):
    PROGRAM = 1,
    DECLARATION_LIST = 2,
    DECLARATION = 3,
    REC_DECLARATION = 4,
    VAR_DECLARATION = 5,
    SCOPED_VAR_DECLARATION = 6,
    VAR_DEC_LIST = 7,
    VAR_DEC_INITIALIZE = 8,
    VAR_DEC_ID = 9,
    SCOPED_TYPE_SPECIFIER = 10,
    TYPE_SPECIFIER = 11,
    RETURN_TYPE_SPECIFIER = 12,
    FUN_DECLARATION = 13,
    PARAMS = 14,
    PARAM_LIST = 15,
    PARAM_TYPE_LIST = 16,
    PARAM_ID_LIST = 17,
    PARAM_ID = 18,
    STATEMENT = 19,
    COMPOUND_STATEMENT = 20,
    LOCAL_DECLARATIONS = 21,
    STATEMENT_LIST = 22,
    EXPRESSION_STATEMENT = 23,
    SELECTION_STATEMENT = 24,
    ITERATION_STATEMENT = 25,
    RETURN_STATEMENT = 26,
    BREAK_STATEMENT = 27,
    EXPRESSION = 28,
    SIMPLE_EXPRESSION = 29,
    AND_EXPRESSION = 30,
    UNARY_REL_EXPRESSION = 31,
    REL_EXPRESSION = 32,
    RELOP = 33,
    SUM_EXPRESSION = 34,
    SUMOP = 35,
    TERM = 36,
    MULOP = 37,
    UNARY_EXPRESSION = 38,
    UNARY_OP = 39,
    FACTOR = 40,
    MUTABLE = 41,
    IMMUTABLE = 42,
    CALL = 43,
    ARGS = 44,
    ARG_LIST = 45,
    CONSTANT = 46,
    LIST_DECLARATION = 47,
    DECLARATIONS_LOCAL = 48,
    LIST_PARAM = 49,
    LIST_ID_PARAM = 50,
    ID_PARAM = 51,
    LIST_VAR_DECL = 52,
    ID_DECL_VAR = 53

class SyntaxNode():
    def __init__(self, node_type):
        if not node_type:
            Exception("Syntax Tree node type does is invalid!")
        
        self.type = node_type
