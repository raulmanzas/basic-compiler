#!/usr/bin/python3

# -*- coding: utf-8 -*-

import argparse
from scanner import Scanner
from parser import Parser
from language import SymbolTable

def main(source_path):
    # All exceptions should be captured here
    try:
        with open(source_path) as source:
            code = source.readlines()
        source.close()
        symbol_table = SymbolTable()
        lexer = Scanner(code, symbol_table)
        lexer.scan()

        if len(lexer.error_list) > 0:
            #TODO: Print error list in a nice way
            print("Lexical erros encountered!!")
        else:
            parser = Parser(symbol_table, lexer)
            parser.parse()
            print("Done!")
    except Exception as e:
        print(e)

# The source code file should be passed as command line parameter
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to the C- source code file")
    args = parser.parse_args()
    
    if args.file:
        main(args.file)
    else:
        #debug only
        main("./testfiles/full_program.c")
        # print("You must supply a C- source code file!")