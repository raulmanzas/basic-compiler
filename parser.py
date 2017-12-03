# -*- coding: utf-8 -*-

from language import SyntaxNode, SyntaxNodeTypes, TokenClass, PatternHelpers

class Parser():
    def __init__(self, symbol_table, scanner):
        self.symbol_table = symbol_table
        self.scanner = scanner
        self.syntax_tree = None
        self.current_token = None
        self.error_list = []
        self.helpers = PatternHelpers()
    
    def register_error(self, token, expected):
        self.error_list.append("Syntax Error in {}:{} expected:'{}' found:'{}'".format(
            token.line, token.column, expected, token.value))
    
    def register_error_if_next_is_not(self,expected_value = None, expected_class = None):
        self.current_token = self.scanner.next_token()
        if expected_class:
            if self.current_token.token_class != expected_class:
                self.register_error(self.current_token, expected_class)
        elif expected_value:
            if self.current_token.value != expected_value:
                self.register_error(self.current_token, expected_value)
    
    def parse(self):
        self.current_token = self.scanner.next_token()
        node = SyntaxNode(SyntaxNodeTypes.PROGRAM)
        node.declaration_list = self.declaration_list()
        return node
    
    def declaration_list(self):
        node = SyntaxNode(SyntaxNodeTypes.DECLARATION_LIST)
        node.declaration = self.declaration()
        node.list_declaration = self.list_declaration()
        return node

    def list_declaration(self):
        node = SyntaxNode(SyntaxNodeTypes.LIST_DECLARATION)
        token_value = self.current_token.value
        declarations = []

        # check if next node is a declaration
        while self.helpers.is_data_type(token_value) or token_value == "record":
            declaration = self.declaration()
            declarations.append(declaration)
        
        if len(declarations) > 0:
            node.list_declaration = declarations
            return node
        return None

    def declaration(self):
        node = SyntaxNode(SyntaxNodeTypes.DECLARATION)
        if self.current_token.token_class == TokenClass.ID:
            node.fun_declaration = self.fun_declaration()
            return node

        token_value = self.current_token.value
        if token_value == "record":
            node.rec_declaration = self.rec_declaration()
            return node
        
        #This verification is tricky. One has to walk to tokens foward to know which rule to apply
        if self.helpers.is_data_type(token_value):
            self.current_token = self.scanner.next_token()
            if self.current_token.token_class == TokenClass.ID:
                next_token = self.scanner.see_next_token()
                self.current_token = self.scanner.prior_token()
                if next_token.value == "(":
                    node.fun_declaration = self.fun_declaration()
                else:
                    node.var_declaration = self.var_declaration()
            return node

        self.register_error(self.current_token, "type declaration")
    
    def rec_declaration(self):
        node = SyntaxNode(SyntaxNodeTypes.REC_DECLARATION)
        self.register_error_if_next_is_not("record")
        self.register_error_if_next_is_not(expected_class=TokenClass.ID)
        node.id = self.current_token
        self.register_error_if_next_is_not("{")        
        node.local_declarations = self.local_declarations()
        self.register_error_if_next_is_not("}")
        return node

    def fun_declaration(self):
        node = SyntaxNode(SyntaxNodeTypes.FUN_DECLARATION)
        if self.helpers.is_data_type(self.current_token.value):
            node.type_specifier = self.type_specifier()
            self.current_token = self.scanner.next_token()
        
        if self.current_token.token_class == TokenClass.ID:
            node.id = self.current_token
            self.register_error_if_next_is_not("(")
            node.params = self.params()
            self.register_error_if_next_is_not(")")
            node.statement = self.statement()
            return node

        self.register_error(self.current_token, "identifier or type specifier")
    
    def var_declaration(self):
        node = SyntaxNodeTypes(SyntaxNodeTypes.VAR_DECLARATION)
        node.type_specifier = self.type_specifier()
        node.var_declaration_list = self.var_declaration_list()
        self.register_error_if_next_is_not(";")
        return node

    def local_declarations(self):
        node = SyntaxNodeTypes(SyntaxNodeTypes.LOCAL_DECLARATIONS)
        node.declarations_local = self.declarations_local()
        return node

    def declarations_local(self):
        node = SyntaxNode(SyntaxNodeTypes.DECLARATIONS_LOCAL)
        token = self.current_token
        declarations = []
        while self.helpers.is_data_type(token) or token.value == "static":
            declaration = self.scoped_var_declaration()
            declarations.append(declaration)
        
        if len(declarations) > 0:
            node.declarations_local = declarations
        return node

    def type_specifier(self):
        node = SyntaxNode(SyntaxNodeTypes.TYPE_SPECIFIER)
        if self.current_token.token_class == TokenClass.ID:
            node.id = self.current_token
        elif self.helpers.is_data_type(self.current_token.value):
            node.return_type_specifier = self.return_type_specifier()
            
        # self.current_token = self.scanner.next_token()
        return node

    def return_type_specifier(self):
        if self.helpers.is_data_type(self.current_token.value):
            node = SyntaxNode(SyntaxNodeTypes.RETURN_TYPE_SPECIFIER)
            node.return_type_specifier = self.current_token
            # self.current_token = self.scanner.next_token()
            return node
        self.register_error(self.current_token, "data type")
        return None
