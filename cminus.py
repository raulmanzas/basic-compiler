#!/usr/bin/python3

# -*- coding: utf-8 -*-

import argparse
from scanner import Scanner
from parser import Parser
from language import SymbolTable, TokenClass

def main(source_path):
    # All exceptions should be captured here
    symbol_table = SymbolTable()
    try:
        with open(source_path) as source:
            code = source.readlines()
        source.close()
        lexer = Scanner(code, symbol_table)
        lexer.scan()

        if len(lexer.error_list) > 0:
            #TODO: Print error list in a nice way
            print("Lexical erros encountered!!")
        else:
            parser = Parser(symbol_table, lexer)
            ast = parser.parse()
            for key, value in symbol_table.hashtable.items():
                print("Key: {0}  Scope: {1}  Type: {2}", key, value.scope, value.datatype)
            if len(parser.error_list) > 0:
                for error in parser.error_list:
                    print(error)
    except Exception as e:
        print(e)
        for key, value in symbol_table.hashtable.items():
            # print(value)
            if value[-1].token_class == TokenClass.ID and hasattr(value[-1], 'data_type'):
                print("Key: {0}  Scope: {1}  Type: {2}".format(key, value[-1].scope, value[-1].data_type))
            else:
                print("key: {0}, Scope: {1} ".format(key, value[-1].scope))

# The source code file should be passed as command line parameter
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to the C- source code file")
    args = parser.parse_args()
    
    if args.file:
        main(args.file)
    else:
        #debug only
        main("./testfiles/semanticErrors.c")
        # print("You must supply a C- source code file!")