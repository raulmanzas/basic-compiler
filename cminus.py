#!/usr/bin/python3

# -*- coding: utf-8 -*-

import argparse
from scanner import Scanner

def main(source_path):
    try:
        with open(source_path) as source:
            code = source.readlines()
        source.close()
        lexer = Scanner(code)
        lexer.scan()
        
    except Exception as e:
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to the C- source code file")
    args = parser.parse_args()
    
    if args.file:
        main(args.file)
    else:
        print("You must supply a C- source code file!")