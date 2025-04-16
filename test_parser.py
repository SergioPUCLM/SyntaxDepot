"""Tester for the lexer / parser output with different files"""
import os
import logging

from src.setup import setup_paths
setup_paths()  # Set up the package paths for local imports

from src.script.lexer import lexer
from src.script.parser import parser


FILENAME = "./src/script/test_code.sds"

def test_lexer():
    """
    Test the lexer with a sample file.
    """
    logging.info("Testing lexer")
    with open(FILENAME, 'r') as f:
        data = f.read()
    
    lexer.input(data)
    
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)


def test_parser():
    """
    Test the parser with a sample file.
    """
    logging.info("Testing parser")
    with open(FILENAME, 'r') as f:
        data = f.read()
    
    result = parser.parse(data)
    print(result)


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting the tests\n")
    # Test the lexer
    #test_lexer()
    # Test the parser
    print("\n")
    test_parser()
