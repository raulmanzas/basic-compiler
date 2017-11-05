# -*- coding: utf-8 -*-

from language import Token, TokenClass

class Scanner():
    def __init__(self, source_code):
        if len(source_code) == 0:
            raise Exception("Source code file is empty")
        self.code = source_code
        self.tokens = []
    
    def is_blank(self, char):
        return char == ' ' or char == '\t' or char == '\n'

    def read_numconst(self, position, line):
        value = ""
        while position < len(line) and line[position].isdigit():
            value += line[position]
            position += 1
        return value, position

    def read_blank(self, position, line):
        while position < len(line) and self.is_blank(line[position]):
            position += 1
        return position

    def scan(self):
        line_pos = 0
        for line in self.code:
            read_pos = 0
            while read_pos < len(line):
                if line[read_pos].isdigit():
                    token_value, read_pos = self.read_numconst(read_pos, line)
                    token = Token(TokenClass.NUMCONST, token_value, line_pos, read_pos)
                    self.tokens.append(token)
                
                elif self.is_blank(line[read_pos]):
                    read_pos = self.read_blank(read_pos, line)
            
            line_pos += 1
        print(self.tokens)
