# -*- coding: utf-8 -*-

import unittest
from language import TokenClass
from scanner import Scanner

class TestScanner(unittest.TestCase):

    def test_can_read_valid_numconst(self):
        mock_code = ["1"]
        scanner = Scanner(mock_code)
        
        token, new_pos = scanner.read_numconst(0, 0)
        self.assertEqual(token.token_class, TokenClass.NUMCONST)
        self.assertEqual(mock_code[0], token.value)
    
    def test_can_read_many_numconst(self):
        mock_code = ["12 35 99"]
        scanner = Scanner(mock_code)
        
        scanner.scan()
        self.assertEqual(len(scanner.tokens), 3)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.NUMCONST)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.NUMCONST)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.NUMCONST)
    
    def test_can_read_numconst_multiple_lines(self):
        mock_code = ["12 35","99"]
        scanner = Scanner(mock_code)
        
        scanner.scan()
        self.assertEqual(len(scanner.tokens), 3)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.NUMCONST)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.NUMCONST)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.NUMCONST)
    
    def test_can_read_charconst(self):
        mock_code = ["'a'"]
        scanner = Scanner(mock_code)
        
        token, new_pos = scanner.read_charconst(0, 0)
        self.assertEqual(token.token_class, TokenClass.CHARCONST)
    
    def test_cant_read_charconst_without_quotes(self):
        mock_code = ["'a"]
        scanner = Scanner(mock_code)
        
        with self.assertRaises(Exception):
            scanner.scan()
    
    def test_can_read_charconst_multiple_lines(self):
        mock_code = ["'a' 'b'","'c'"]
        scanner = Scanner(mock_code)
        
        scanner.scan()
        self.assertEqual(len(scanner.tokens), 3)
        self.assertEqual(scanner.tokens[0].token_class, TokenClass.CHARCONST)
        self.assertEqual(scanner.tokens[1].token_class, TokenClass.CHARCONST)
        self.assertEqual(scanner.tokens[2].token_class, TokenClass.CHARCONST)
    
    def test_can_read_charconst_empty(self):
        mock_code = ["''"]
        scanner = Scanner(mock_code)

        token, new_pos = scanner.read_charconst(0, 0)
        self.assertEqual(token.token_class, TokenClass.CHARCONST)
        self.assertEqual(new_pos, 2)
    
    def test_can_read_separator(self):
        mock_code = [","]
        scanner = Scanner(mock_code)

        token, new_pos = scanner.read_separator(0, 0)
        self.assertEqual(TokenClass.SEPARATOR, token.token_class)
    
    def test_can_read_separators_multiple_lines(self):
        mock_code = [",", ";", "{"]
        scanner = Scanner(mock_code)
        scanner.scan()
        
        self.assertEqual(len(scanner.tokens), 3)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[0].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[1].token_class)
        self.assertEqual(TokenClass.SEPARATOR, scanner.tokens[2].token_class)
    
    def test_can_read_separators_multiple_lines(self):
        mock_code = [", { ( } ) ] ; . ["]
        scanner = Scanner(mock_code)
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
        

if __name__ == '__main__':
    unittest.main()
