# -*- coding: utf-8 -*-

from language import Token, TokenClass, PatternHelpers

class Scanner():
    def __init__(self, source_code):
        if len(source_code) == 0:
            raise Exception("Source code file is empty")
        self.helper = PatternHelpers()
        self.code = source_code
        self.tokens = []
    
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
            msg = "Couldn't understant '{}' in {}:{}".format(value, line_pos, position)
            raise Exception(msg)

    def read_blank(self, position, line):
        while position < len(line) and self.helper.is_blank(line[position]):
            position += 1
        return position

    def read_separator(self, position, line_pos):
        line = self.code[line_pos]
        value = line[position]
        if self.helper.is_separator(value):
            position += 1
            return Token(TokenClass.SEPARATOR, value, line_pos, position), position

        msg = "Couldn't understant '{}' in {}:{}".format(value, line_pos, position)
        raise Exception(msg)
    
    def read_operator(self, position, line_pos):
        line = self.code[line_pos]
        value = line[position]
        if self.helper.is_operator(value):
            position += 1
            if position < len(line) and self.helper.is_operator(value + line[position]):
                value += line[position]
                position += 1
                return Token(TokenClass.OPERATOR, value, line_pos, position), position
            return Token(TokenClass.OPERATOR, value, line_pos, position), position
        
        msg = "Couldn't understant '{}' in {}:{}".format(value, line_pos, position)
        raise Exception(msg)

    def scan(self):
        line_pos = 0
        for line in self.code:
            read_pos = 0
            while read_pos < len(line):
                if line[read_pos].isdigit():
                    token, read_pos = self.read_numconst(read_pos, line_pos)
                    self.tokens.append(token)
                
                elif self.helper.is_blank(line[read_pos]):
                    read_pos = self.read_blank(read_pos, line)
                
                elif line[read_pos] == "'":
                    token, read_pos = self.read_charconst(read_pos, line_pos)
                    self.tokens.append(token)
                
                elif self.helper.is_separator(line[read_pos]):
                    token, read_pos = self.read_separator(read_pos, line_pos)
                    self.tokens.append(token)
                
                elif self.helper.is_comment(line, read_pos):
                    read_pos = len(line)

                elif self.helper.is_operator(line[read_pos]):
                    token, read_pos = self.read_operator(read_pos, line_pos)
                    self.tokens.append(token)
                
            line_pos += 1