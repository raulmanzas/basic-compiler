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
    
    def parse(self):
        node = SyntaxNode(SyntaxNodeTypes.PROGRAM)
        # node.declaration_list = self.declaration_list()
    
    def register_error(self, token, expected):
        self.error_list.append("Syntax Error in {}:{} expected:'{}' found:'{}'".format(
            token.line, token.column, expected, token.value))

