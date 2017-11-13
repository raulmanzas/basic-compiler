# -*- coding: utf-8 -*-

class Parser():
    def __init__(self, symbol_table, scanner):
        self.symbol_table = symbol_table
        self.scanner = scanner
    
    def parse(self):
        print("Parsing!!!!!!!1!!")