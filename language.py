# -*- coding: utf-8 -*-

from enum import Enum
import copy

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

    def is_unary_operator(self, char):
        unary_operators = ["-", "*", "?"]
        return char in unary_operators

    def is_mulop(self, char):
        mul_ops = ["*", "/", "%"]
        return char in mul_ops

    def is_sumop(self, char):
        sum_ops = ["+", "-"]
        return char in sum_ops

    def is_relational_operator(self, char):
        relational_operators = ["<=", "<", ">", ">=", "==", "!="]
        return char in relational_operators

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

    def is_contracted_operator(self, lexeme):
        ops = ["++", "--"]
        return lexeme in ops

    def is_assignment_operator(self, lexeme):
        ops = ['=', '+=', '-=', '*=', '/=']
        return lexeme in ops

    def is_constant_token(self, token):
        if token.token_class == TokenClass.NUMCONST or token.token_class == TokenClass.CHARCONST:
            return True
        return token.value == "true" or token.value == "false"

    def is_statement_token(self, token):
        #check the grammar definition to understand this
        pattern_starters = ["{", "if", "while", "break", "return"]
        if token.token_class == TokenClass.ID:
            return True
        return token.value in pattern_starters

    def is_rel_expression_token(self, token):
        if token.token_class == TokenClass.ID:
            return True
        if token.token_class == TokenClass.NUMCONST:
            return True
        if token.token_class == TokenClass.CHARCONST:
            return True
        return self.is_unary_operator(token.value) or token.value == "("


class SymbolTable():
    def __init__(self):
        self.hashtable = {}
        self.current_scope = 0
    
    def store(self, token):
        token.scope = self.current_scope
        if token.value not in self.hashtable:
            self.hashtable[token.value] = [token]
        else:
            # Verify if that id exists in the same scope
            tk_list = self.hashtable[token.value]
            if len(tk_list) == 1 and token.scope == 0:
                return
            for tk in tk_list:
                if tk.scope == self.current_scope:
                    raise Exception("Name already exists in scope!")
            tk_list.append(token)
    
    def lookup(self, value):
        if self.hashtable[value]:
            tk_list = self.hashtable[value]
            return tk_list[-1] #pop of the stack
        return None

    def set_type(self, token, data_type):
        new_token = copy.copy(token)
        new_token.data_type = data_type
        self.store(new_token)
    
    def push_scope(self):
        self.current_scope += 1
    
    def kill_scope(self):
        for key, tk_list in self.hashtable.items():
            if tk_list[-1].scope == self.current_scope:
                tk_list.pop()
        self.current_scope -= 1
    
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
    ID_DECL_VAR = 53,
    INITIALIZE_DECL_VAR = 54,
    EXPRESSION_SIMPLE = 55,
    EXPRESSION_AND = 56,
    EXPRESSION_REL = 57,
    NEW_MUTABLE = 58,
    LIST_ARG = 59,
    NEW_TERM = 60,
    EXPRESSION_SUM = 61,
    LIST_STATEMENT = 62,
    STATEMENT_SELECTION = 63,

class SyntaxNode():
    def __init__(self, node_type):
        if not node_type:
            Exception("Syntax Tree node type does is invalid!")
        
        self.type = node_type
    
    def __str__(self):
        return "{}".format(self.type)

class SemanticHelpers():
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def assign_value(self, token, const):
        if not const:
            return
        if const.token_class == TokenClass.ID:
            return self.assign_id_to_id(token, const)

        token = self.symbol_table.lookup(token.value)
        if const.token_class == TokenClass.CHARCONST and token.data_type == "char":
            token.variable_value = const
            return
        if const.token_class == TokenClass.NUMCONST and token.data_type == "int":
            token.variable_value = const
            return
        if const.value == "true" or const.value == "false" and token.data_type == "bool":
            token.variable_value = const
            return
        raise Exception("Invalid type assignment!")
    
    def assign_id_to_id(self, left_id, right_id):
        left_token = self.symbol_table.lookup(left_id.value)
        right_token = self.symbol_table.lookup(right_id.value)
        if left_token.data_type != right_token.data_type:
            raise Exception("Invalid type assignment!")
        left_token.variable_value = right_token.value
        return

    def validate_type(self, func_id, return_token):
        func_type = self.symbol_table.lookup(func_id.value).data_type
        if return_token.token_class == TokenClass.ID:
            return_type = self.symbol_table.lookup(return_token.value).data_type
            if func_type == return_type:
                return
        if return_token.token_class == TokenClass.CHARCONST:
            if func_type == 'char':
                return
        if return_token.token_class == TokenClass.NUMCONST:
            if func_type == 'int':
                return
        raise Exception("Return type should be '{0}'".format(func_type))
    
    def is_valid_variable(self, variable_id):
        var_token = self.symbol_table.lookup(variable_id.value)
        if hasattr(var_token, "data_type"):
            return
        raise Exception("Variable '{0}' wasn't declared".format(variable_id.value))