# -*- coding: utf-8 -*-

from language import *

class Parser():
    def __init__(self, symbol_table, scanner):
        self.symbol_table = symbol_table
        self.scanner = scanner
        self.semantic_helpers = SemanticHelpers(symbol_table)
        self.syntax_tree = None
        self.current_token = None
        self.error_list = []
        self.last_data_type = None
        self.last_constant = None
        self.last_id = None
        self.last_func_id = None
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
    
    def register_error_if_current_is_not(self, expected_value = None, expected_class = None):
        #should validate if expected class is a valid class?
        if expected_value:
            if self.current_token.value != expected_value:
                self.register_error(self.current_token, expected_value)
        elif expected_class:
            if self.current_token.token_class != expected_class:
                self.register_error(self.current_token, expected_class)
        try:
            self.current_token = self.scanner.next_token()
        except Exception:
            return None

    def parse(self):
        self.current_token = self.scanner.next_token()
        node = SyntaxNode(SyntaxNodeTypes.PROGRAM)
        # empty source code should just return the root node
        if self.current_token == None:
            return node
        self.symbol_table.push_scope()
        node.declaration_list = self.declaration_list()
        self.symbol_table.kill_scope()
        return node
    
    def declaration_list(self):
        node = SyntaxNode(SyntaxNodeTypes.DECLARATION_LIST)
        node.declaration = self.declaration()
        node.list_declaration = self.list_declaration()
        return node

    def list_declaration(self):
        node = SyntaxNode(SyntaxNodeTypes.LIST_DECLARATION)
        declarations = []

        # check if next node is a declaration
        while self.helpers.is_data_type(self.current_token.value) or self.current_token.value == "record":
            declaration = self.declaration()
            declarations.append(declaration)
            # self.current_token = self.scanner.next_token()
        
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
            else:
                self.register_error(self.current_token, "identifier")
            return node

        self.register_error(self.current_token, "type declaration")
        return node
    
    def rec_declaration(self):
        node = SyntaxNode(SyntaxNodeTypes.REC_DECLARATION)
        self.register_error_if_current_is_not("record")
        if self.current_token.token_class != TokenClass.ID:
            self.register_error(self.current_token, "identifier")
            # self.current_token = self.scanner.next_token()
        else:
            node.id = self.current_token
        self.register_error_if_next_is_not("{")
        self.symbol_table.push_scope()
        node.local_declarations = self.local_declarations()
        self.register_error_if_current_is_not("}")
        self.symbol_table.kill_scope()
        return node

    def fun_declaration(self):
        node = SyntaxNode(SyntaxNodeTypes.FUN_DECLARATION)
        if self.helpers.is_data_type(self.current_token.value):
            node.type_specifier = self.type_specifier()
            self.current_token = self.scanner.next_token()
        
        if self.current_token.token_class == TokenClass.ID:
            node.id = self.current_token
            self.symbol_table.set_type(node.id, self.last_data_type)
            self.last_id = node.id
            self.last_func_id = node.id
            self.register_error_if_next_is_not("(")
            self.current_token = self.scanner.next_token()
            node.params = self.params()
            self.register_error_if_current_is_not(")")
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
        # node.declarations_local = self.declarations_local()
        return self.declarations_local()

    def declarations_local(self):
        node = SyntaxNode(SyntaxNodeTypes.DECLARATIONS_LOCAL)
        # self.current_token = self.scanner.next_token()
        token = self.current_token
        declarations = []
        while self.helpers.is_data_type(self.current_token.value) or self.current_token.value == "static":
            declaration = self.scoped_var_declaration()
            declarations.append(declaration)
        if len(declarations) > 0:
            node.declarations_local = declarations
        return node

    def scoped_var_declaration(self):
        node = SyntaxNode(SyntaxNodeTypes.SCOPED_VAR_DECLARATION)
        node.scoped_type_specifier = self.scoped_type_specifier()
        node.var_decl_list = self.var_decl_list()
        self.register_error_if_current_is_not(";")
        # self.register_error_if_next_is_not(";")
        # self.current_token = self.scanner.next_token()
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
        self.semantic_helpers.assign_value(self.last_id, self.last_constant)
        return node

    def initialize_decl_var(self):
        node = SyntaxNode(SyntaxNodeTypes.INITIALIZE_DECL_VAR)
        if self.current_token.value == "=":
            self.current_token = self.scanner.next_token()
            node.simple_expression = self.simple_expression()
            return node
        return node

    def var_decl_id(self):
        node = SyntaxNode(SyntaxNodeTypes.VAR_DEC_ID)
        self.register_error_if_next_is_not(expected_class=TokenClass.ID)
        node.id = self.current_token
        # Sets the datatype in the symboltable for future reference
        self.symbol_table.set_type(node.id, self.last_data_type)
        self.last_id = node.id
        self.current_token = self.scanner.next_token()
        node.id_decl_var = self.id_decl_var()
        return node

    def id_decl_var(self):
        node = SyntaxNode(SyntaxNodeTypes.ID_DECL_VAR)
        if self.current_token.value == "[":
            self.current_token = self.scanner.next_token()
            node.id_decl_var = self.current_token
            self.register_error_if_next_is_not("]")
            self.current_token = self.scanner.next_token() #last change
            return node
        return node

    def list_var_decl(self):
        node = SyntaxNode(SyntaxNodeTypes.LIST_VAR_DECL)
        var_declarations = []
        # next_token = self.scanner.see_next_token()
        while self.scanner.see_next_token().token_class == TokenClass.ID:
            if self.current_token.value != ",":
                self.register_error(self.current_token, ",")
            # last_token.value = ""
            # self.current_token = self.scanner.next_token()
            decl = self.var_decl_initialize()
            var_declarations.append(decl)
            # self.current_token = self.scanner.next_token()
        
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
            self.last_data_type = self.current_token.value
        elif self.helpers.is_data_type(self.current_token.value):
            node.return_type_specifier = self.return_type_specifier()
            
        # self.current_token = self.scanner.next_token()
        return node

    def return_type_specifier(self):
        if self.helpers.is_data_type(self.current_token.value):
            node = SyntaxNode(SyntaxNodeTypes.RETURN_TYPE_SPECIFIER)
            node.return_type_specifier = self.current_token
            self.last_data_type = self.current_token.value
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
            # self.register_error_if_current_is_not(")")
            # self.current_token = self.scanner.next_token()
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
        # self.current_token = self.scanner.next_token()
        node.list_id_param = self.list_id_param()
        return node

    def param_id(self):
        node = SyntaxNode(SyntaxNodeTypes.PARAM_ID)
        self.register_error_if_next_is_not(expected_class=TokenClass.ID)
        node.id = self.current_token
        self.symbol_table.set_type(node.id, self.last_data_type)
        self.last_id = node.id
        self.current_token = self.scanner.next_token()
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
        ids = []
        
        while self.scanner.see_next_token().token_class == TokenClass.ID:
            id_param = self.param_id()
            ids.append(id_param)
            self.register_error_if_next_is_not(",")
            self.current_token = self.scanner.next_token()
        
        if len(ids) > 0:
            node.list_id_param = ids
        return node

    def list_param(self):
        node = SyntaxNode(SyntaxNodeTypes.LIST_PARAM)
        if self.helpers.is_data_type(self.scanner.see_next_token().value):
            self.register_error_if_current_is_not(";")
        list_params = []
        while self.helpers.is_data_type(self.current_token.value):
            param_type_list = self.param_type_list()
            list_params.append(param_type_list)
            # self.current_token = self.scanner.next_token()
        
        if len(list_params) > 0:
            node.list_param = list_params
        return node

    def constant(self):
        node = SyntaxNode(SyntaxNodeTypes.CONSTANT)
        if self.current_token.token_class == TokenClass.NUMCONST:
            node.num_const = self.current_token
            self.last_constant = node.num_const
            return node
        if self.current_token.token_class == TokenClass.CHARCONST:
            node.char_const = self.current_token
            self.last_constant = node.char_const
            return node
        if self.current_token.value == "true" or self.current_token.value == "false":
            node.boolean = self.current_token
            self.last_constant = node.boolean
            return node
        self.register_error(self.current_token, "data literal")
        return None
    
    def arg_list(self):
        node = SyntaxNode(SyntaxNodeTypes.ARG_LIST)
        node.expression = self.expression()
        node.list_arg = self.list_arg()
        return node

    def list_arg(self):
        node = SyntaxNode(SyntaxNodeTypes.LIST_ARG)
        expressions = []
        while self.current_token.value == ",":
            self.current_token = self.scanner.next_token()
            expression = self.expression()
            expressions.append(expression)
            self.current_token = self.scanner.next_token()
        
        if len(expressions) > 0:
            node.expression = expressions
        return node
    def call(self):
        node = SyntaxNode(SyntaxNodeTypes.CALL)
        if self.current_token.token_class != TokenClass.ID:
            self.register_error(self.current_token, "identifier")
        else:
            node.id = self.current_token
            self.last_id = node.id
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
            self.current_token = self.scanner.next_token()
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

        if self.helpers.is_rel_expression_token(self.current_token):
            node.rel_expression = self.rel_expression()
            return node
        if self.current_token.value in ["true", "false"]:
            # self.current_token = self.scanner.prior_token()
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
            self.current_token = self.scanner.next_token()
            node.sum_expression = self.sum_expression()
            return node
        return node

    def relop(self):
        node = SyntaxNode(SyntaxNodeTypes.RELOP)
        if self.helpers.is_relational_operator(self.current_token.value):
            node.relop = self.current_token
            return node

        self.register_error(self.current_token, "relational operator")
        return node

    def unary_op(self):
        node = SyntaxNode(SyntaxNodeTypes.UNARY_OP)
        if self.helpers.is_unary_operator(self.current_token.value):
            node.unary_op = self.current_token
            self.current_token = self.scanner.next_token()
            return node
        
        self.register_error(self.current_token, "unary operator")
        return node

    def mulop(self):
        node = SyntaxNode(SyntaxNodeTypes.MULOP)
        if self.helpers.is_mulop(self.current_token.value):
            node.mulop = self.current_token
            self.current_token = self.scanner.next_token()
            return node
        
        self.register_error(self.current_token, "multiplication operator")
        return node

    def sumop(self):
        node = SyntaxNode(SyntaxNodeTypes.SUMOP)
        if self.helpers.is_sumop(self.current_token.value):
            node.sumop = self.current_token
            self.current_token = self.scanner.next_token()
            return node
        
        self.register_error(self.current_token, "summation operator")
        return node

    def immutable(self):
        node = SyntaxNode(SyntaxNodeTypes.IMMUTABLE)
        if self.current_token.value == "(":
            node.expression = self.expression()
            self.register_error_if_next_is_not(")")
            return node
        elif self.current_token.token_class == TokenClass.ID:
            node.call = self.call()
            return node
        elif self.helpers.is_constant_token(self.current_token):
            node.constant = self.constant()
            self.current_token = self.scanner.next_token()
            return node
        else:
            self.register_error(self.current_token, "immutable expression")
            return node

    def mutable(self):
        node = SyntaxNode(SyntaxNodeTypes.MUTABLE)
        if self.current_token.token_class == TokenClass.ID:
            node.id = self.current_token
            self.semantic_helpers.is_valid_variable(node.id)
            self.last_id = node.id
            self.current_token = self.scanner.next_token()
            node.new_mutable = self.new_mutable()
            return node

        self.register_error(self.current_token, "identification")
        return node

    def new_mutable(self):
        node = SyntaxNode(SyntaxNodeTypes.NEW_MUTABLE)
        ids = []
        expressions = []
        while self.current_token.value == "[" or self.current_token.value == ".":
            if self.current_token.value == "[":
                self.current_token = self.scanner.next_token()
                expression = self.expression()
                expressions.append(expression)
                self.register_error_if_current_is_not("]")
                # self.current_token = self.scanner.next_token()
            elif self.current_token.value == ".":
                self.current_token = self.scanner.next_token()
                tk_id = self.current_token
                ids.append(tk_id)
                self.current_token = self.scanner.next_token()
        
        if len(ids) > 0:
            node.ids = ids
        if len(expressions) > 0:
            node.expressions = expressions
        return node

    def factor(self):
        node = SyntaxNode(SyntaxNodeTypes.FACTOR)
        token = self.current_token
        # next_token = self.scanner.see_next_token()
        if self.helpers.is_constant_token(token) or token.value == "(":
            # self.current_token = self.scanner.next_token()
            node.immutable = self.immutable()
            return node
        
        elif self.current_token.token_class == TokenClass.ID:
            next_token = self.scanner.see_next_token()
            if next_token.value == "(":
                node.immutable = self.immutable()
                return node
            elif next_token.value == "[" or next_token.value == ".":
                node.mutable = self.mutable()
                return node
            else:
                node.id = self.current_token
                self.current_token = self.scanner.next_token()
                # self.register_error(self.current_token, "mutable or immutable structure")
                return node
        
    def term(self):
        node = SyntaxNode(SyntaxNodeTypes.TERM)
        node.unary_expression = self.unary_expression()
        node.new_term = self.new_term()
        return node

    def new_term(self):
        node = SyntaxNode(SyntaxNodeTypes.NEW_TERM)
        ops = []
        unary_expressions = []
        while self.helpers.is_mulop(self.current_token.value):
            op = self.mulop()
            ops.append(op)
            unary_expression = self.unary_expression()
            unary_expressions.append(unary_expression)
            # self.current_token = self.scanner.next_token()
        
        if len(ops) > 0:
            node.mulop = ops
        if len(unary_expressions) > 0:
            node.unary_expression = unary_expressions
        return node

    def unary_expression(self):
        node = SyntaxNode(SyntaxNodeTypes.UNARY_EXPRESSION)
        ops = []
        if self.helpers.is_unary_operator(self.current_token.value):
            while self.helpers.is_unary_operator(self.current_token.value):
                op = self.unary_op()
                ops.append(op)
                self.current_token = self.scanner.next_token()
            if len(ops) > 0:
                node.unary_op = ops
        else:
            node.factor = self.factor()
        return node

    def sum_expression(self):
        node = SyntaxNode(SyntaxNodeTypes.SUM_EXPRESSION)
        node.term = self.term()
        node.expression_sum = self.expression_sum()
        return node

    def expression_sum(self):
        node = SyntaxNode(SyntaxNodeTypes.EXPRESSION_SUM)
        ops = []
        terms = []
        while self.helpers.is_sumop(self.current_token.value):
            op = self.sumop()
            ops.append(op)
            term = self.term()
            terms.append(term)
        
        if len(ops) > 0:
            node.sumop = ops
        if len(terms) > 0:
            node.term = terms
        return node

    def statement_list(self):
        node = SyntaxNode(SyntaxNodeTypes.STATEMENT_LIST)
        node.list_statement = self.list_statement()
        return node

    def expression_stmt(self):
        node = SyntaxNode(SyntaxNodeTypes.EXPRESSION_STATEMENT)
        if self.current_token.value == ";":
            node.expression = self.current_token
            return node
        elif self.current_token.token_class == TokenClass.ID:
            node.expression = self.expression()
            self.register_error_if_current_is_not(';')
            return node
        else:
            self.register_error(self.current_token, "; or identifier")
            return node
    
    def compound_stmt(self):
        node = SyntaxNode(SyntaxNodeTypes.COMPOUND_STATEMENT)
        self.register_error_if_current_is_not("{")
        self.symbol_table.push_scope()
        node.local_declarations = self.local_declarations()
        node.statement_list = self.statement_list()
        if self.current_token.value == "}":
            self.symbol_table.kill_scope()
            self.current_token = self.scanner.next_token()
        # self.register_error_if_current_is_not("}")
        return node

    def selection_stmt(self):
        node = SyntaxNode(SyntaxNodeTypes.SELECTION_STATEMENT)
        self.register_error_if_current_is_not("if")
        self.register_error_if_current_is_not("(")
        node.simple_expression = self.simple_expression()
        self.register_error_if_current_is_not(")")
        node.statement = self.statement()
        node.stmt_selection = self.stmt_selection()
        return node

    def stmt_selection(self):
        node = SyntaxNode(SyntaxNodeTypes.STATEMENT_SELECTION)
        if self.current_token.value == "else":
            self.current_token = self.scanner.next_token()
            node.statement = self.statement()
            return node
        return node

    def return_statement(self):
        node = SyntaxNode(SyntaxNodeTypes.RETURN_STATEMENT)
        if self.current_token.value != "return":
            self.register_error(self.current_token, "return")
        self.current_token = self.scanner.next_token()
        
        if self.current_token.value == ";":
            return node
        else:
            node.expression = self.expression()
            if(self.scanner.see_prior_token().token_class == TokenClass.ID):
                self.semantic_helpers.validate_type(self.last_func_id, self.last_id)
            else:
                self.semantic_helpers.validate_type(self.last_func_id, self.last_constant)
            if self.current_token.value != ";":
                self.register_error(self.current_token, ";")
            self.current_token = self.scanner.next_token()
            return node
    
    def iteration_stmt(self):
        node = SyntaxNode(SyntaxNodeTypes.ITERATION_STATEMENT)
        if self.current_token.value != "while":
            self.register_error(self.current_token, "while statement")
        self.register_error_if_next_is_not("(")
        self.current_token = self.scanner.next_token()
        node.simple_expression = self.simple_expression()
        self.register_error_if_current_is_not(")")
        node.statement = self.statement()
        return node

    def list_statement(self):
        node = SyntaxNode(SyntaxNodeTypes.LIST_STATEMENT)
        statements = []
        while self.helpers.is_statement_token(self.current_token):
            statement = self.statement()
            # self.register_error_if_current_is_not(";")
            statements.append(statement)
        
        if len(statements) > 0:
            node.statement = statements
        return node

    def statement(self):
        node = SyntaxNode(SyntaxNodeTypes.STATEMENT)
        if self.current_token.token_class == TokenClass.ID:
            node.expression_stmt = self.expression_stmt()
            return node
        if self.current_token.value == "{":
            node.compound_stmt = self.compound_stmt()
            return node
        if self.current_token.value == "if":
            node.selection_stmt = self.selection_stmt()
            return node
        if self.current_token.value == "while":
            node.iteration_stmt = self.iteration_stmt()
            return node
        if self.current_token.value == "return":
            node.return_statement = self.return_statement()
            return node
        if self.current_token.value == "break":
            node.break_statement = self.break_statement()
            return node
        self.register_error(self.current_token, "valid statement")
        return node

    def expression(self):
        node = SyntaxNode(SyntaxNodeTypes.EXPRESSION)
        if self.current_token.token_class == TokenClass.ID:
            next_token = self.scanner.see_next_token()
            if next_token.value == '(':
                node.simple_expression = self.simple_expression()
                return node
            node.mutable = self.mutable()
            if self.helpers.is_contracted_operator(self.current_token.value):
                node.op = self.current_token
                self.current_token = self.scanner.next_token()
                return node
            if self.helpers.is_assignment_operator(self.current_token.value):
                node.op = self.current_token
                self.current_token = self.scanner.next_token()
                left_id = self.last_id
                node.expression = self.expression()
                if left_id.value == self.last_id.value:
                    self.semantic_helpers.assign_value(left_id, self.last_constant)
                else:
                    self.semantic_helpers.assign_value(left_id, self.last_id)
                return node
            if self.helpers.is_sumop(self.current_token.value):
                node.expression_sum = self.expression_sum()
                return node
            return node
        if self.current_token.value == '(' or self.helpers.is_constant_token(self.current_token):
            node.simple_expression = self.simple_expression()
            return node
        if self.helpers.is_logical_operator(self.current_token.value):
            node.simple_expression = self.simple_expression()
            return node
        self.register_error(self.current_token, 'valid expression')