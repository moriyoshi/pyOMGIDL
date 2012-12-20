import os
from pyomgidl.reader.lexer import *
from pyomgidl.reader.parser import *
from pyomgidl.reader.tree import pp
from pyomgidl.reader.preprocessor import preprocess
from pyomgidl.reader.exceptions import *

def initializePLY():
    lexer()
    parser()

def parse_into_ast(f, source=None, webidl=False, **kwargs):
    return parser(webidl=webidl).parse(preprocess(f, source), lexer(webidl=webidl))
