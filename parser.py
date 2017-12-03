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
        node.var_declaration_list = self.var_decl_list()
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

    def scoped_var_declaration(self):
        node = SyntaxNode(SyntaxNodeTypes.SCOPED_VAR_DECLARATION)
        node.scoped_type_specifier = self.scoped_type_specifier()
        node.var_decl_list = self.var_decl_list()
        self.register_error_if_next_is_not(";")
        return node

    def var_decl_list(self):
        node = SyntaxNode(SyntaxNodeTypes.VAR_DEC_LIST)
        node.var_decl_initialize = self.var_decl_initialize()
        node.list_var_decl = self.list_var_decl()
        return node

    def var_decl_initialize(self):
        node = SyntaxNode(SyntaxNodeTypes.VAR_DEC_INITIALIZE)
        node.var_decl_id = self.var_decl_id()
        node.initialize_decl_var = self.initialize_decl_var()
        return node

    def initialize_decl_var(self):
        node = SyntaxNode(SyntaxNodeTypes.INITIALIZE_DECL_VAR)
        if self.current_token.value == ":":
            self.current_token = self.scanner.next_token()
            node.simple_expression = self.simple_expression()
            return node
        return node

    def var_decl_id(self):
        node = SyntaxNode(SyntaxNodeTypes.VAR_DEC_ID)
        self.register_error_if_next_is_not(expected_class=TokenClass.ID)
        node.id = self.current_token
        node.id_decl_var = self.id_decl_var()
        return node

    def id_decl_var(self):
        node = SyntaxNode(SyntaxNodeTypes.ID_DECL_VAR)
        if self.current_token.value == "[":
            node.id_decl_var = self.current_token
            self.register_error_if_next_is_not("]")
            return node
        return node

    def list_var_decl(self):
        node = SyntaxNode(SyntaxNodeTypes.LIST_VAR_DECL)
        var_declarations = []
        next_token = self.scanner.see_next_token()
        while next_token.token_class == TokenClass.ID:
            if self.current_token.value != ",":
                self.register_error(self.current_token, ",")
            self.current_token = self.scanner.next_token()
            decl = self.var_decl_initialize()
            var_declarations.append(decl)
            self.current_token = self.scanner.next_token()
        
        if len(var_declarations) > 0:
            node.list_var_decl = var_declarations
        return node

    def scoped_type_specifier(self):
        node = SyntaxNode(SyntaxNodeTypes.SCOPED_TYPE_SPECIFIER)
        if self.current_token.value == "static":
            self.current_token = self.scanner.next_token()
        node.type_specifier = self.type_specifier()
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
    
    def params(self):
        node = SyntaxNode(SyntaxNodeTypes.PARAMS)
        node.param_list = self.param_list()
        return node

    def param_list(self):
        if self.helpers.is_data_type(self.current_token.value):
            node = SyntaxNode(SyntaxNodeTypes.PARAM_LIST)
            node.param_type_list = self.param_type_list()
            node.list_param = self.list_param()
            return node
        return None

    def param_type_list(self):
        node = SyntaxNode(SyntaxNodeTypes.PARAM_TYPE_LIST)
        node.type_specifier = self.type_specifier()
        node.param_id_list = self.param_id_list()
        return node

    def param_id_list(self):
        node = SyntaxNode(SyntaxNodeTypes.PARAM_ID_LIST)
        node.param_id = self.param_id()
        node.list_id_param = self.list_id_param()
        return node

    def param_id(self):
        node = SyntaxNode(SyntaxNodeTypes.PARAM_ID)
        self.register_error_if_next_is_not(expected_class=TokenClass.ID)
        node.id = self.current_token
        node.idParam = self.id_param()
        return node

    def id_param(self):
        node = SyntaxNode(SyntaxNodeTypes.ID_PARAM)
        if self.current_token.value == "[":
            self.register_error_if_next_is_not("]")
            node.id_param = self.current_token
            return node
        return node

    def list_id_param(self):
        node = SyntaxNode(SyntaxNodeTypes.LIST_ID_PARAM)
        self.register_error_if_next_is_not(",")
        ids = []
        while self.current_token.token_class == TokenClass.ID:
            id_param = self.param_id()
            ids.append(id_param)
            self.register_error_if_next_is_not(",")
            self.current_token = self.scanner.next_token()
        
        if len(ids) > 0:
            node.list_id_param = ids
        return node

    def list_param(self):
        node = SyntaxNode(SyntaxNodeTypes.LIST_PARAM)
        self.register_error_if_next_is_not(";")
        list_params = []
        while self.helpers.is_data_type(self.current_token.value):
            param_type_list = self.param_type_list()
            list_params.append(param_type_list)
            self.current_token = self.scanner.next_token()
        
        if len(list_params) > 0:
            node.list_param = list_params
        return node

    def constant(self):
        node = SyntaxNode(SyntaxNodeTypes.CONSTANT)
        if self.current_token.token_class == TokenClass.NUMCONST:
            node.num_const = self.current_token
            return node
        if self.current_token.token_class == TokenClass.CHARCONST:
            node.char_const = self.current_token
            return node
        if self.current_token.value == "true" or self.current_token.value == "false":
            node.boolean = self.current_token
            return node
        self.register_error(self.current_token, "data literal")
        return None
    
    def arg_list(self):
        node = SyntaxNode(SyntaxNodeTypes.ARG_LIST)
        node.expression = self.expression()
        node.list_arg = self.list_arg()
        return node

    def call(self):
        node = SyntaxNode(SyntaxNodeTypes.CALL)
        if self.current_token.token_class != TokenClass.ID:
            self.register_error(self.current_token, "identifier")
        else:
            node.id = self.current_token
        self.current_token = self.scanner.next_token()
        self.register_error_if_next_is_not("(")
        node.args = self.args()
        self.register_error_if_next_is_not(")")
        return node

    def args(self):
        node = SyntaxNode(SyntaxNodeTypes.ARGS)
        if self.current_token.token_class == TokenClass.ID:
            node.arg_list = self.arg_list()
            self.current_token = self.scanner.next_token()
        return node

    def break_statement(self):
        node = SyntaxNode(SyntaxNodeTypes.BREAK_STATEMENT)
        if self.current_token.value == "break":
            node.break_statement = self.current_token
            self.register_error_if_next_is_not(";")
            return node

        self.register_error(self.current_token, "break statement")
        return node

    def simple_expression(self):
        node = SyntaxNode(SyntaxNodeTypes.SIMPLE_EXPRESSION)
        node.and_expression = self.and_expression()
        node.expression_simple = self.expression_simple()
        return node

    def expression_simple(self):
        node = SyntaxNode(SyntaxNodeTypes.EXPRESSION_SIMPLE)
        exprs = []
        while self.current_token.value == "or":
            node.or_op = self.current_token
            self.current_token = self.scanner.next_token()
            expr = self.and_expression()
            exprs.append(expr)
            self.current_token = self.scanner.next_token()
        
        if len(exprs) > 0:
            node.expression_simple = exprs
        return node

    def and_expression(self):
        node = SyntaxNode(SyntaxNodeTypes.AND_EXPRESSION)
        node.unary_rel_expression = self.unary_rel_expression()
        node.expression_and = self.expression_and()
        return node

    def expression_and(self):
        node = SyntaxNode(SyntaxNodeTypes.EXPRESSION_AND)
        exprs = []
        while self.current_token.value == "and":
            node.and_op = self.current_token
            self.current_token = self.scanner.next_token()
            expr = self.unary_rel_expression()
            exprs.append(expr)
            self.current_token = self.scanner.next_token()
        
        if len(exprs) > 0:
            node.expression_and = exprs
        return node

    def unary_rel_expression(self):
        node = SyntaxNode(SyntaxNodeTypes.UNARY_REL_EXPRESSION)
        if self.current_token.value == "not":
            node.not_op = self.current_token
            self.current_token = self.scanner.next_token()
            node.unary_rel_expression = self.unary_rel_expression()
            return node

        if self.current_token.token_class == TokenClass.ID or
            self.helpers.is_unary_operator(self.current_token.value) or
            self.current_token.value == "(":
            node.rel_expression = self.rel_expression()
            return node

        self.register_error(self.current_token, "relational operator")
        return node

    def rel_expression(self):
        node = SyntaxNode(SyntaxNodeTypes.REL_EXPRESSION)
        node.sum_expression = self.sum_expression()
        node.expression_rel = self.expression_rel()
        return node

    def expression_rel(self):
        node = SyntaxNode(SyntaxNodeTypes.EXPRESSION_REL)
        if self.helpers.is_relational_operator(self.current_token.value):
            node.relop = self.relop()
            node.sum_expression = self.sum_expresison()
            return node
        return node

    def relop(self):
        node = SyntaxNode(SyntaxNodeTypes.RELOP)
        if self.helpers.is_relational_operator(self.current_token.value):
            node.relop = self.current_token
            return node

        self.register_error(self.current_token, "relational operator")
        return node
