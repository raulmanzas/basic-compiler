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

    def read_numconst(self, position, line_pos):
        value = ""
        line = self.code[line_pos]
        while position < len(line) and line[position].isdigit():
            value += line[position]
            position += 1
        return Token(TokenClass.NUMCONST, value, line_pos, position - 1), position

    def read_charconst(self, position, line_pos):
        line = self.code[line_pos]
        position += 1
        
        # Char can be just a ''
        if line[position] == "'":
            return Token(TokenClass.CHARCONST, '', line_pos, position), position + 1
            
        value = line[position]
        position +=1
        if position < len(line) and line[position] == "'":
            return Token(TokenClass.CHARCONST, value, line_pos, position), position + 1
        else:
            msg = "Couldn't understant '{}' in {}:{}".format(line[position], line_pos, position)
            raise Exception(msg)

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
                    token, read_pos = self.read_numconst(read_pos, line_pos)
                    self.tokens.append(token)
                
                elif self.is_blank(line[read_pos]):
                    read_pos = self.read_blank(read_pos, line)
                
                elif line[read_pos] == "'":
                    token, read_pos = self.read_charconst(read_pos, line_pos)
                    self.tokens.append(token)
            
            line_pos += 1
        print(self.tokens)
