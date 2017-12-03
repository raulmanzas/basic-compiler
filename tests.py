# -*- coding: utf-8 -*-

import unittest
from language import TokenClass, SymbolTable
from scanner import Scanner
from parser import Parser

class TestScanner(unittest.TestCase):

    def get_scanner(self, mock_code):
        symbol_table = SymbolTable()
        return Scanner(mock_code, symbol_table)

    def test_can_read_valid_numconst(self):
        mock_code = ["1"]
        scanner = self.get_scanner(mock_code)
        
        token, new_pos = scanner.read_numconst(0, 0)
        self.assertEqual(token.token_class, TokenClass.NUMCONST)
        self.assertEqual(mock_code[0], token.value)
    
    def test_can_read_many_numconst(self):
        mock_code = ["12 35 99"]
        scanner = self.get_scanner(mock_code)
        
        scanner.scan()
        self.assertEqual(len(scanner.tokens), 3)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.NUMCONST)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.NUMCONST)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.NUMCONST)
    
    def test_can_read_numconst_multiple_lines(self):
        mock_code = ["12 35","99"]
        scanner = self.get_scanner(mock_code)
        
        scanner.scan()
        self.assertEqual(len(scanner.tokens), 3)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.NUMCONST)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.NUMCONST)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.NUMCONST)
    
    def test_can_read_charconst(self):
        mock_code = ["'a'"]
        scanner = self.get_scanner(mock_code)
        
        token, new_pos = scanner.read_charconst(0, 0)
        self.assertEqual(token.token_class, TokenClass.CHARCONST)
    
    def test_cant_read_charconst_without_quotes(self):
        mock_code = ["'a"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()
        self.assertNotEqual(scanner.error_list, [])
        self.assertEqual(len(scanner.error_list), 1)
    
    def test_can_read_charconst_multiple_lines(self):
        mock_code = ["'a' 'b'","'c'"]
        scanner = self.get_scanner(mock_code)
        
        scanner.scan()
        self.assertEqual(len(scanner.tokens), 3)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.CHARCONST)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.CHARCONST)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.CHARCONST)
    
    def test_can_read_charconst_empty(self):
        mock_code = ["''"]
        scanner = self.get_scanner(mock_code)

        token, new_pos = scanner.read_charconst(0, 0)
        self.assertEqual(token.token_class, TokenClass.CHARCONST)
        self.assertEqual(new_pos, 2)
    
    def test_can_read_separator(self):
        mock_code = [","]
        scanner = self.get_scanner(mock_code)

        token, new_pos = scanner.read_separator(0, 0)
        self.assertEqual(TokenClass.SEPARATOR, token.token_class)
    
    def test_can_read_separators_multiple_lines(self):
        mock_code = [",", ";", "{"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()
        
        self.assertEqual(len(scanner.tokens), 3)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[0].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[1].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[2].token_class)
    
    def test_can_read_separators_multiple_lines(self):
        mock_code = [", { ( } ) ] ; . ["]
        scanner = self.get_scanner(mock_code)
        scanner.scan()
        
        self.assertEqual(len(scanner.tokens), 9)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[0].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[1].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[2].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[3].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[4].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[5].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[6].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[7].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[8].token_class)
    
    def test_can_read_operator(self):
        mock_code = ["="]
        scanner = self.get_scanner(mock_code)
        
        token, new_pos = scanner.read_operator(0, 0)
        self.assertEqual(TokenClass.OPERATOR, token.token_class)
    
    def test_can_read_2part_operator(self):
        mock_code = ["+="]
        scanner = self.get_scanner(mock_code)

        token, new_pos = scanner.read_operator(0, 0)
        self.assertEqual(TokenClass.OPERATOR, token.token_class)
    
    def test_can_read_multiple_operators(self):
        mock_code = ["+ *= >= ?"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()

        self.assertEqual(len(scanner.tokens), 4)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.OPERATOR)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.OPERATOR)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.OPERATOR)
        self.assertEqual(scanner.tokens[3].token_class, TokenClass.OPERATOR)
    
    def test_can_read_logical_operators(self):
        mock_code = ["and"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()

        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.OPERATOR)
    
    def test_can_read_multiple_operators(self):
        mock_code = ["- /", "== <="]
        scanner = self.get_scanner(mock_code)
        scanner.scan()

        self.assertEqual(len(scanner.tokens), 4)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.OPERATOR)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.OPERATOR)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.OPERATOR)
        self.assertEqual(scanner.tokens[3].token_class, TokenClass.OPERATOR)
    
    def test_can_read_multiple_logical_operators(self):
        mock_code = ["and", "or", "not and"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()

        self.assertEqual(len(scanner.tokens), 4)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.OPERATOR)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.OPERATOR)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.OPERATOR)
        self.assertEqual(scanner.tokens[3].token_class, TokenClass.OPERATOR)

    def test_can_ignore_comments(self):
        mock_code = ["123 //id do usuario"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()

        self.assertEqual(len(scanner.tokens), 1)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.NUMCONST)
    
    def test_can_read_keyword(self):
        mock_code = ["static"]
        scanner = self.get_scanner(mock_code)

        token, pos = scanner.try_read_keyword(0, 0)
        self.assertNotEqual(token, None)
        self.assertEqual(token.token_class, TokenClass.KEYWORD)
    
    def test_can_read_multiple_keywords(self):
        mock_code = ["static int if else"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()

        self.assertEqual(len(scanner.tokens), 4)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.KEYWORD)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.KEYWORD)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.KEYWORD)
        self.assertEqual(scanner.tokens[3].token_class, TokenClass.KEYWORD)
    
    def test_can_read_keywords_multiple_lines(self):
        mock_code = ["static int", "if else"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()

        self.assertEqual(len(scanner.tokens), 4)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.KEYWORD)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.KEYWORD)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.KEYWORD)
        self.assertEqual(scanner.tokens[3].token_class, TokenClass.KEYWORD)
    
    def test_can_read_id(self):
        mock_code = ["teste"]
        scanner = self.get_scanner(mock_code)
        
        token, pos = scanner.try_read_id(0, 0)
        self.assertEqual(token.token_class, TokenClass.ID)
    
    def test_can_read_id_with_numbers(self):
        mock_code = ["teste112"]
        scanner = self.get_scanner(mock_code)
        
        token, pos = scanner.try_read_id(0, 0)
        self.assertEqual(token.token_class, TokenClass.ID)
    
    def test_can_read_multiple_id(self):
        mock_code = ["teste112 abc12"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()
        
        self.assertEqual(len(scanner.tokens), 2)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.ID)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.ID)
    
    def test_can_read_multiple_lines_id(self):
        mock_code = ["teste112 abc12", "sim123"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()
        
        self.assertEqual(len(scanner.tokens), 3)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.ID)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.ID)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.ID)
    
    # def test_cant_read_id_starting_with_number(self):
    #     mock_code = ["112andre"]
    #     scanner = self.get_scanner(mock_code)
        
    #     with self.assertRaises(Exception):
    #         scanner.scan()
    
    def test_can_store_symbol_table(self):
        mock_code = ["identifier"]
        scanner = self.get_scanner(mock_code)
        scanner.scan()

        self.assertEqual(scanner.symbol_table.lookup("identifier").token_class, TokenClass.ID)
        self.assertEqual(len(scanner.symbol_table.hashtable), 1)

class TestParser(unittest.TestCase):

    def get_parser(self, mock_code):
        symbol_table = SymbolTable()
        scanner = Scanner(mock_code, symbol_table)
        scanner.scan()
        parser = Parser(symbol_table, scanner)
        return parser

    def test_can_parse_var_declaration(self):
        mock_code = ["record point{ int x, y;}"]
        parser = self.get_parser(mock_code)
        parser.parse()

if __name__ == '__main__':
    unittest.main()
