# lexer.py
#
# The rules contained by this file is taken from libIDL's lexer.l.
# 
# Copyright (C) 1998, 1999 Andrew T. Veliath
#               2012 Moriyoshi Koizumi
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free
# Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import re
from ply import lex
from pyomgidl.reader.exceptions import IDLSyntaxError

__all__ = [
    'lexer',
    'states',
    'tokens',
    ]

states = [
    ('CFRG', 'exclusive'),
    ('CFRGX', 'exclusive'),
    ('XP', 'exclusive'),
    ('PROP', 'exclusive'),
    ('NATIVE', 'exclusive'),
    ('NATIVETYPE', 'exclusive'),
    ]

tokens = [
    'TOK_ANY',
    'TOK_ATTRIBUTE',
    'TOK_BOOLEAN',
    'TOK_CASE',
    'TOK_CHAR',
    'TOK_CONST',
    'TOK_CONTEXT',
    'TOK_DEFAULT',
    'TOK_DOUBLE',
    'TOK_ENUM',
    'TOK_EXCEPTION',
    'TOK_FALSE',
    'TOK_FIXED',
    'TOK_FLOAT',
    'TOK_IN',
    'TOK_INOUT',
    'TOK_INTERFACE',
    'TOK_LONG',
    'TOK_MODULE',
    'TOK_NATIVE',
    'TOK_OBJECT',
    'TOK_OCTET',
    'TOK_ONEWAY',
    'TOK_OP_SCOPE',
    'TOK_OP_SHL',
    'TOK_OP_SHR',
    'TOK_OUT',
    'TOK_RAISES',
    'TOK_READONLY',
    'TOK_SEQUENCE',
    'TOK_SHORT',
    'TOK_STRING',
    'TOK_STRUCT',
    'TOK_SWITCH',
    'TOK_TRUE',
    'TOK_TYPECODE',
    'TOK_TYPEDEF',
    'TOK_VALUETYPE',
    'TOK_UNION',
    'TOK_UNSIGNED',
    'TOK_VARARGS',
    'TOK_VOID',
    'TOK_WCHAR',
    'TOK_WSTRING',
    'TOK_FLOATP',
    'TOK_INTEGER',
    'TOK_PROP_VALUE',
    'TOK_NATIVE_TYPE',
    'TOK_IDENT',
    'TOK_SQSTRING',
    'TOK_DQSTRING',
    'TOK_FIXEDP',
    'TOK_CODEFRAG',
    'TOK_COLON',
    'TOK_SEMICOLON',
    'TOK_COMMA',
    'TOK_LBRACE',
    'TOK_RBRACE',
    'TOK_LPAREN',
    'TOK_RPAREN',
    'TOK_CARET',
    'TOK_AMPERSAND',
    'TOK_PLUS',
    'TOK_MINUS',
    'TOK_ASTERISK',
    'TOK_SLASH',
    'TOK_PERCENT',
    'TOK_TILDE',
    'TOK_LSQB',
    'TOK_RSQB',
    'TOK_LT',
    'TOK_GT',
    'TOK_EQUAL',
    'TOK_QUESTION',
    'TOK_OPTIONAL',
    ]

t_TOK_COLON = r':'
t_TOK_SEMICOLON = r';'
t_TOK_COMMA = r','
t_TOK_LBRACE = r'\{'
t_TOK_RBRACE = r'\}'
t_TOK_LPAREN = r'\('
t_TOK_RPAREN = r'\)'
t_TOK_CARET = r'\^'
t_TOK_AMPERSAND = r'&'
t_TOK_PLUS = r'\+'
t_TOK_MINUS = r'-'
t_TOK_ASTERISK = r'\*'
t_TOK_SLASH = r'/'
t_TOK_PERCENT = r'%'
t_TOK_TILDE = r'~'
t_TOK_LSQB = r'\['
t_TOK_RSQB = r'\]'
t_TOK_LT = r'<'
t_TOK_GT = r'>'
t_TOK_EQUAL = r'='
t_TOK_OP_SCOPE = r'::'
t_TOK_OP_SHL = r'<<'
t_TOK_OP_SHR = r'>>'
t_TOK_QUESTION = r'\?'

common_string_tokens = {
    'any': 'TOK_ANY',
    'attribute': 'TOK_ATTRIBUTE',
    'boolean': 'TOK_BOOLEAN',
    'case': 'TOK_CASE',
    'const': 'TOK_CONST',
    'context': 'TOK_CONTEXT',
    'default': 'TOK_DEFAULT',
    'double': 'TOK_DOUBLE',
    'enum': 'TOK_ENUM',
    'exception': 'TOK_EXCEPTION',
    'false': 'TOK_FALSE',
    'float': 'TOK_FLOAT',
    'fixed': 'TOK_FIXED',
    'in': 'TOK_IN',
    'inout': 'TOK_INOUT',
    'interface': 'TOK_INTERFACE',
    'long': 'TOK_LONG',
    'module': 'TOK_MODULE',
    'native': 'TOK_NATIVE',
    'object': 'TOK_OBJECT',
    'octet': 'TOK_OCTET',
    'oneway': 'TOK_ONEWAY',
    'out': 'TOK_OUT',
    'raises': 'TOK_RAISES',
    'readonly': 'TOK_READONLY',
    'sequence': 'TOK_SEQUENCE',
    'short': 'TOK_SHORT',
    'string': 'TOK_STRING',
    'struct': 'TOK_STRUCT',
    'switch': 'TOK_SWITCH',
    'true': 'TOK_TRUE',
    'typecode': 'TOK_TYPECODE',
    'typedef': 'TOK_TYPEDEF',
    'union': 'TOK_UNION',
    'unsigned': 'TOK_UNSIGNED',
    'varargs': 'TOK_VARARGS',
    'valuetype': 'TOK_VALUETYPE',
    'void': 'TOK_VOID',
    'wstring': 'TOK_WSTRING',
    'TypeCode': 'TOK_TYPECODE',
    'Object': 'TOK_OBJECT',
    }

omgidl_string_tokens = {
    'char': 'TOK_CHAR',
    'wchar': 'TOK_WCHAR',
    }

def t_TOK_OCTAL(t):
    r'''0[0-9]+'''
    t.type = 'TOK_INTEGER'
    return t

def t_TOK_HEXDECIMAL(t):
    r'''0[xX][0-9A-Fa-f]+'''
    t.type = 'TOK_INTEGER'
    return t

def t_TOK_FLOATP(t):
    r'''(?:(?:0|[1-9][0-9]*)?\.[0-9]+|(?P<int_part>0|[1-9][0-9]*))(?P<exp_part>[eE]-?[0-9]+)?(?P<fixed>[dD])?'''
    int_part = t.lexer.lexmatch.group('int_part')
    exp_part = t.lexer.lexmatch.group('exp_part')
    fixed_part = t.lexer.lexmatch.group('fixed')
    if fixed_part is not None:
        t.type = 'TOK_FIXEDP'
    else:
        if int_part is not None and exp_part is None:
            t.type = 'TOK_INTEGER'
        else:
            t.type = 'TOK_FLOATP'
    return t

t_PROP_TOK_PROP_VALUE = r'''\([^)]*\)'''

def t_PROP_TOK_RSQB(t):
    r'\]'
    t.lexer.pop_state()
    return t

t_TOK_SQSTRING = r"""'(?:[^']|\\')*'"""
t_TOK_DQSTRING = r'''"(?:[^"]|\\")*"'''

def t_INITIAL_PROP_NATIVE_TOK_IDENT(t):
    r'''[A-Za-z_][A-Za-z0-9_]*'''
    t_type = common_string_tokens.get(t.value)
    if t_type is not None:
        t.type = t_type
    else:
        if t.lexer.webidl:
            if t.value == 'optional':
                t.type = 'TOK_OPTIONAL'
        else:
            t_type = omgidl_string_tokens.get(t.value)
            if t_type is not None:
                t.type = t_type
    if t_type == 'TOK_NATIVE':
        t.lexer.push_state('NATIVE') 
    return t

def t_INITIAL_NATIVE_PROP_WHITESPACE(t):
    r'''[ \t\v\f]+'''

def t_NATIVE_TOK_SEMICOLON(t):
    r';'
    t.lexer.pop_state()
    return t

def t_NATIVE_TOK_LPAREN(t):
    r'\('
    t.lexer.pop_state()
    t.lexer.push_state('NATIVETYPE')
    return t

def t_NATIVETYPE_TOK_RPAREN(t):
    r'\)'
    t.lexer.pop_state()
    return t

def t_NATIVETYPE_TOK_NATIVE_TYPE(t):
    r'''[^);]+'''
    return t

def t_INITIAL_XP_CFRG_BEGIN_CODEFRAG(t):
    r'''%\{'''
    t.lexer.push_state('CFRGX')

def t_CFRGX_TOK_CODEFRAG(t):
    r'''%\}'''
    t.lexer.pop_state()
    return t

def t_CFRGX_X(t):
    r'''.*'''
    t.type = TOK_CODEFRAG
    return t

def t_ANY_TOK_PRAGMA(t):
    r'''(?:(?<=[\r\n])|^)[ \t\v\f]*\#[ \t\v\f]*pragma[ \t\v\f]*(?P<pragma>[^\r\n]*)(?:\r\n|\r|\n|$)'''
    pragma = t.lexer.lexmatch.group('pragma')
    pragma_values = re.match(r'([^ \t\v\f]+)(?:[ \t\v\f]+(.*))?', pragma)
    if pragma_values:
        t.lexer.pragma[pragma_values.group(1)] = pragma_values.group(2)
    t.lexer.lineno += 1

def t_ANY_TOK_SRCFILE(t):
    r'''(?:(?<=[\r\n])|^)[ \t\v\f]*\#[ \t\v\f]*(?:line[ \t\v\f]*)?(?P<lineno>[0-9][0-9]*)[^\r\n]*(?:\r\n|\r|\n)'''
    t.lexer.lineno = int(t.lexer.lexmatch.group('lineno'))

def t_ANY_NEWLINE(t):
    r'''\r|\n|\r\n'''
    t.lexer.lineno += 1

def t_ANY_LINE_COMMENT(t):
    r'''//.*'''

def t_ANY_BLOCK_COMMENT(t):
    r'''/\*(?:[^/]|[^*]/)*\*/'''

def t_ANY_error(t):
    raise IDLSyntaxError('Illegal token (state=%s): %s' % (t.lexer.lexstate, t.value), t.lexer.lineno)

def lexer(webidl=False, **kwargs):
    retval = lex.lex(lextab='lextab', optimize=1, outputdir=os.path.dirname(__file__), **kwargs)
    retval.webidl = webidl
    retval.pragma = {}
    return retval
