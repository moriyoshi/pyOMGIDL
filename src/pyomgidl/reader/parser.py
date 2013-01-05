# parser.py
#
# The rules contained by this grammar file is taken from libIDL's parser.y .
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
#

import os
import re
from ply import yacc
from pyomgidl.reader.exceptions import IDLSyntaxError
from pyomgidl.reader.lexer import tokens
from pyomgidl.reader.tree import *

__all__ = [
    'parser',
    ]

def p_specification(p):
    '''
    specification :
        | definition_list
    '''
    p[0] = len(p) == 2 and Specification(p[1]) or Specification()

def p_z_definition_list(p):
    '''
    z_definition_list :
        | definition_list
    '''
    p[0] = len(p) == 2 and p[1] or []

def p_definition_list(p):
    '''
    definition_list : definition
        | definition_list definition
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_useless_semicolon(p):
    '''
    useless_semicolon : TOK_SEMICOLON
    '''

def p_illegal_ident(p):
    '''
    illegal_ident : scoped_name
    '''

def p_definition(p):
    '''
    definition : type_decl TOK_SEMICOLON
        | const_decl TOK_SEMICOLON
        | except_decl TOK_SEMICOLON
        | interface TOK_SEMICOLON
        | module TOK_SEMICOLON
        | codefrag
        | illegal_ident
        | useless_semicolon
    '''
    p[0] = p[1]

def p_module(p):
    '''
    module : TOK_MODULE ident TOK_LBRACE z_definition_list TOK_RBRACE
    '''
    pragma_prefix = p.lexer.pragma.pop('prefix', None)
    if pragma_prefix is not None:
        prefix_match = re.match(r'"((?:[^"]|\\")*)"|\'((?:[^\']|\\\')*)\'', pragma_prefix)
        if not prefix_match:
            raise_syntax_error(p, "Invalid value specified for #pragma prefix: %s" % pragma_prefix)
        prefix = prefix_match.group(1) or prefix_match.group(2)
        if prefix != "":
            prefix += "."
    else:
        prefix = ""
    p[2].value = prefix + p[2].value
    p[0] = Module(name=p[2], definitions=p[4])

def p_interface_cache_ident(p):
    '''
    interface_catch_ident : ident
        | TOK_OBJECT
        | TOK_TYPECODE
    '''
    if isinstance(p[1], basestring):
        value = p[1].lower()
        if value == 'object':
            raise_syntax_error(p, "Interfaces cannot be named `Object'")
        elif value == 'typecode':
            raise_syntax_error(p, "Interfaces cannot be named `TypeCode'")
    p[0] = p[1]

def p_interface(p):
    '''
    interface : modifiers_and_props TOK_INTERFACE interface_catch_ident z_inheritance TOK_LBRACE interface_body TOK_RBRACE
        | modifiers_and_props TOK_INTERFACE interface_catch_ident
    '''
    if p[1][0]:
        raise_syntax_error(p, 'No modifiers are allowed for interface')
    p[0] = Interface(properties=p[1][1], name=p[3], supers=(len(p) > 4 and p[4] or None), body=(len(p) > 4 and p[6] or None))

def p_inheritance(p):
    '''
    z_inheritance :
        | TOK_COLON scoped_name_list
    '''
    p[0] = len(p) != 1 and p[2] or []

def p_scoped_name_list(p):
    '''
    scoped_name_list : scoped_name
        | scoped_name_list TOK_COMMA scoped_name
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_interface_body(p):
    '''
    interface_body : export_list
    '''
    p[0] = p[1]

def p_export_list(p):
    '''
    export_list :
        | export_list export
    '''
    if len(p) == 1:
        p[0] = []
    else:
        if p[2] is not None:
            p[1].append(p[2])
        p[0] = p[1]

def p_export(p):
    '''
    export : type_decl TOK_SEMICOLON
        | except_decl TOK_SEMICOLON
        | op_decl TOK_SEMICOLON
        | attr_decl TOK_SEMICOLON
        | const_decl TOK_SEMICOLON
        | codefrag
        | useless_semicolon
    '''
    p[0] = p[1]

def p_type_decl(p):
    '''
    type_decl : typedef_decl
        | struct_type
        | union_type
        | enum_type
        | valuetype_decl
        | dictionary_decl
        | callback_decl
        | native_decl
    '''
    p[0] = p[1]

def p_typedef_decl(p):
    '''
    typedef_decl : modifiers_and_props TOK_TYPEDEF type_declarator
    '''
    p[0] = TypeDef(type=p[3][0], declarators=p[3][1], properties=p[1][1])

def p_native_decl(p):
    '''
    native_decl : modifiers_and_props TOK_NATIVE simple_declarator z_native_type
    '''
    p[0] = NativeDecl(declarator=p[3], native_type=p[4], properties=p[1][1])

def p_z_native_type(p):
    '''
    z_native_type :
        | TOK_LPAREN TOK_NATIVE_TYPE TOK_RPAREN
    '''
    p[0] = len(p) != 1 and p[2] or None

def p_type_declarator(p):
    '''
    type_declarator : type_spec declarator_list
    '''
    p[0] = (p[1], p[2])

def p_type_spec(p):
    '''
    type_spec : simple_type_spec
        | constr_type_spec
    '''
    p[0] = p[1]

def p_simple_type_spec(p):
    '''
    simple_type_spec : base_type_spec
        | template_type_spec
        | scoped_name
    '''
    p[0] = p[1]

def p_constr_type_spec(p):
    ''' 
    constr_type_spec : struct_type
        | union_type
        | enum_type
    '''
    p[0] = p[1]

def p_z_ident_catch(p):
    '''
    z_ident_catch :
        | ident
    '''
    p[0] = len(p) == 2 and p[1] or None

def p_struct_type(p):
    '''
    struct_type : modifiers_and_props TOK_STRUCT z_ident_catch TOK_LBRACE struct_member_list TOK_RBRACE
    ''' 

def p_valuetype_decl(p):
    '''
    valuetype_decl : modifiers_and_props TOK_VALUETYPE z_ident_catch z_value_inheritance_spec z_valuetype_body
    '''
    p[0] = ValueType(properties=p[1][1], name=p[3], super=p[4], body=p[5])

def p_z_value_inheritance_spec(p):
    '''
    z_value_inheritance_spec :
        | value_inheritance_spec
    '''
    p[0] = len(p) == 2 and p[1] or None

def p_value_inheritance_spec(p):
    '''
    value_inheritance_spec : type_spec
    '''
    p[0] = p[1]

def p_z_valuetype_body(p):
    '''
    z_valuetype_body :
        | TOK_LBRACE valuetype_member_list TOK_RBRACE
    '''
    p[0] = len(p) == 4 and p[2] or None

def p_valuetype_member_list(p):
    '''
    valuetype_member_list :
        | valuetype_member_list valuetype_member
    '''
    if len(p) == 1:
        p[0] = []
    else:
        if p[2] is not None:
            p[1].append(p[2])
            p[0] = p[1]

def p_valuetype_member(p):
    '''
    valuetype_member : type_decl TOK_SEMICOLON
        | except_decl TOK_SEMICOLON
        | attr_decl TOK_SEMICOLON
        | const_decl TOK_SEMICOLON
        | member 
        | codefrag
        | useless_semicolon
    '''
    p[0] = p[1]

def p_union_type(p):
    '''
    union_type : modifiers_and_props TOK_UNION z_ident_catch TOK_SWITCH TOK_LPAREN switch_type_spec TOK_RPAREN TOK_LBRACE switch_body TOK_RBRACE
    '''

def p_switch_type_spec(p):
    '''
    switch_type_spec : integer_type
        | char_type
        | boolean_type
        | enum_type
        | scoped_name
    '''
    p[0] = p[1]

def p_switch_body(p):
    '''
    switch_body : case_stmt_list
    '''

def p_case_stmt_list(p):
    '''
    case_stmt_list : case_stmt
        | case_stmt_list case_stmt
    '''

def p_case_stmt(p):
    '''
    case_stmt : case_label_list element_spec TOK_SEMICOLON
    '''

def p_element_spec(p):
    '''
    element_spec : type_spec declarator
    '''

def p_case_label_list(p):
    '''
    case_label_list : case_label
        | case_label_list case_label
    '''

def p_case_label(p):
    '''
    case_label : TOK_CASE const_exp ':'
        | TOK_DEFAULT ':'
    '''

def p_const_decl(p):
    '''
    const_decl : modifiers_and_props TOK_CONST const_type ident TOK_EQUAL const_exp
    '''
    p[0] = ConstDecl(name=p[4], type=p[3], value=p[6], properties=p[1])

def p_except_decl(p):
    '''
    except_decl : modifiers_and_props TOK_EXCEPTION ident TOK_LBRACE except_member_list TOK_RBRACE
    '''
    p[0] = ExceptionDecl(name=p[3], members=p[5], properties=p[1][1])

def p_except_member_list(p):
    '''
    except_member_list :
        | except_member_list member
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_dictionary_decl(p):
    '''
    dictionary_decl : modifiers_and_props TOK_DICTIONARY z_ident_catch z_value_inheritance_spec z_dictionary_body
    '''

def p_z_dictionary_body(p):
    '''
    z_dictionary_body :
        | TOK_LBRACE dictionary_member_list TOK_RBRACE
    '''
    p[0] = len(p) == 4 and p[2] or None

def p_dictionary_member_list(p):
    '''
    dictionary_member_list :
        | dictionary_member_list dictionary_member
    '''

def p_dictionary_member(p):
    '''
    dictionary_member : modifiers_and_props op_param_type_spec_with_nullable  simple_declarator_pair_list TOK_SEMICOLON
    '''

def p_callback_decl(p):
    '''
    callback_decl : modifiers_and_props TOK_CALLBACK TOK_EQUAL op_type_spec parameter_decls
    '''

def p_attr_decl(p):
    '''
    attr_decl : modifiers_and_props TOK_ATTRIBUTE z_props op_param_type_spec_with_nullable attr_declarator_list
    '''
    p[0] = AttrDef(type=p[4][0], modifiers=p[1][0], nullable=p[4][1], declarators=p[5], properties=p[1][1] + p[3])

def p_attr_declarator_list(p):
    '''
    attr_declarator_list : attr_declarator
        | attr_declarator_list TOK_COMMA attr_declarator
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_attr_declarator(p):
    '''
    attr_declarator : simple_declarator attr_raises_spec_list
    '''
    p[0] = AttrDeclarator(p[1], p[2][0], p[2][1])


def p_attr_raises_spec_list(p):
    '''
    attr_raises_spec_list :
        | attr_raises_spec_list attr_raises_spec
    '''
    if len(p) == 1:
        p[0] = ([], [])
    else:
        if p[2][0] == 'getter':
            p[1][0].extend(p[2][1])
        elif p[2][0] == 'setter':
            p[1][1].extend(p[2][1])
        p[0] = p[1]

def p_attr_raises_spec(p):
    '''
    attr_raises_spec : TOK_GETTER raises
        | TOK_SETTER raises
    '''
    p[0] = (p[1], p[2])

def p_param_type_spec(p):
    '''
    param_type_spec : op_param_type_spec_with_nullable
        | TOK_VOID
    '''
    if p[1] == 'void':
        p[0] = (BasicTypeNode('void'), True)
    else:
        p[0] = p[1]

def p_op_param_type_spec_illegal(p):
    '''
    op_param_type_spec_illegal : sequence_type
    '''
    raise_syntax_error(p, 'Illegal type specified for parameter or attribute: %s' % p[1])

def p_z_nullable(p):
    '''
    z_nullable : TOK_QUESTION
        |
    '''
    p[0] = len(p) > 1

def p_op_param_type_spec_with_nullable(p):
    '''
    op_param_type_spec_with_nullable : op_param_type_spec z_nullable
    '''
    p[0] = (p[1], p[2])

def p_op_param_type_spec(p):
    '''
    op_param_type_spec : base_type_spec
        | string_type
        | wide_string_type
        | fixed_pt_type
        | scoped_name
        | op_param_type_spec_illegal
    '''
    p[0] = p[1]

def p_modifiers_and_props(p):
    '''
    modifiers_and_props :
        | modifiers_and_props op_modifier_or_prop
    '''
    if len(p) == 1:
        p[0] = ([], [])
    else:
        for modifier in p[2]:
            if isinstance(modifier, Property):
                if modifier in p[1][1]:
                    raise_syntax_error(p, "Property `%s' applied more than once" % modifier.key)
                p[1][1].append(modifier)
            else:
                if modifier in p[1][0]:
                    raise_syntax_error(p, "Duplicate `%s' modifier" % modifier)
                p[1][0].append(modifier)
        p[0] = p[1]

def p_op_modifier_or_prop(p):
    '''
    op_modifier_or_prop : TOK_ONEWAY
        | TOK_STATIC
        | TOK_READONLY
        | TOK_LSQB enter_prop prop_hash optional_trailing_comma TOK_RSQB
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[3]

def p_op_decl(p):
    '''
    op_decl : modifiers_and_props op_type_spec ident parameter_decls z_raises z_context
    '''
    p[0] = OperationDef(name=p[3], return_type=p[2], parameters=p[4], raises=p[5], modifiers=p[1][0], context=p[6], properties=p[1][1])

def p_op_type_spec(p):
    '''
    op_type_spec : op_param_type_spec
        | TOK_VOID
    '''
    if p[1] == 'void':
        p[0] = BasicTypeNode('void')
    else:
        p[0] = p[1]

def p_is_varargs(p):
    '''
    is_varargs :
        | TOK_VARARGS
        | TOK_ELLIPSIS
    '''
    p[0] = len(p) != 1 and Parameter(name='*', type=BasicTypeNode('any'), nullable=False, direction=['in'], default_value=None, properties=None) or None

def p_is_cvarargs(p):
    '''
    is_cvarargs :
        | TOK_COMMA TOK_VARARGS
        | TOK_COMMA TOK_ELLIPSIS
    '''
    p[0] = len(p) != 1 and Parameter(name='*', type=BasicTypeNode('any'), nullable=False, direction=['in'], default_value=None, properties=None) or None

def p_parameter_decls(p):
    '''
    parameter_decls : TOK_LPAREN param_decl_list is_cvarargs TOK_RPAREN
        | TOK_LPAREN is_varargs TOK_RPAREN
        | TOK_LPAREN param_attributes_and_props param_type_spec TOK_ELLIPSIS simple_declarator TOK_RPAREN
    '''
    if len(p) == 4:
        p[0] = Parameters(items=[], varargs=p[2])
    elif len(p) == 5:
        p[0] = Parameters(items=p[2], varargs=p[3])
    else:
        attributes, props = p[2]

        if len(attributes) != 0 and (len(attributes) != 1 or attributes[0] != 'in'):
            raise_syntax_error(p, "`out' direction specified for a typed variable argument")
        p[0] = Parameters(items=[], varargs=Parameter(name='*', type=p[3][0], nullable=p[3][1], direction=['in'], default_value=None, properties=props))

def p_param_decl_list(p):
    '''
    param_decl_list : param_decl
        | param_decl_list TOK_COMMA param_decl
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_z_default_value(p):
    '''
    z_default_value :
        | TOK_EQUAL const_exp
    '''
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = p[2]

def p_param_decl(p):
    '''
    param_decl : param_attributes_and_props param_type_spec simple_declarator z_default_value
    '''
    attributes, props = p[1]
    type_spec = p[2]
    name = p[3]
    default_value = p[4] 

    if 'optional' in attributes:
        attributes.remove('optional')
        optional = True
    else:
        optional = False
    if not attributes:
        if not p.parser.webidl:
            raise_syntax_error(p, "Missing direction attribute")
    if not optional and default_value is not None:
        raise_syntax_error(p, "Default value present for non-optional parameter")
    p[0] = Parameter(name=name, type=type_spec[0], nullable=type_spec[1], direction=attributes, default_value=default_value, properties=props)

def p_param_attributes_and_props(p):
    '''
    param_attributes_and_props :
        | param_attributes_and_props param_attribute_and_prop
    '''
    if len(p) == 1:
        p[0] = ([], [])
    else:
        for attribute in p[2]:
            if isinstance(attribute, Property):
                if attribute in p[1][1]:
                    raise_syntax_error(p, "Property `%s' applied more than once" % attribute.key)
                p[1][1].append(attribute)
            else:
                if attribute in p[1][0]:
                    raise_syntax_error(p, "Duplicate parameter attribute `%s" % attribute)
                p[1][0].append(attribute)
        p[0] = p[1]

def p_param_attribute_and_prop(p):
    '''
    param_attribute_and_prop : TOK_IN
        | TOK_OUT
        | TOK_INOUT
        | TOK_OPTIONAL
        | TOK_LSQB enter_prop prop_hash TOK_RSQB
    '''
    if len(p) == 5:
        p[0] = [p[3]]
    else:
        if p[1] == 'in':
            p[0] = ['in']
        elif p[1] == 'out':
            p[0] = ['out']
        elif p[1] == 'inout':
            p[0] = ['in', 'out']
        elif p[1] == 'optional':
            p[0] = ['optional']

def p_z_raises(p):
    '''
    z_raises :
        | raises
    '''
    p[0] = len(p) != 1 and p[1] or None

def p_z_context(p):
    '''
    z_context :
        | context
    '''
    p[0] = len(p) != 1 and p[1] or None

def p_raises(p):
    '''
    raises : TOK_RAISES TOK_LPAREN scoped_name_list TOK_RPAREN
    '''
    p[0] = p[3]

def p_context(p):
    '''
    context : TOK_CONTEXT TOK_LPAREN string_lit_list TOK_RPAREN
    '''
    p[0] = p[3]

def p_const_type(p):
    '''
    const_type : integer_type
        | char_type
        | octet_type
        | wide_char_type
        | boolean_type
        | floating_pt_type
        | string_type
        | wide_string_type
        | fixed_pt_const_type
        | scoped_name
    '''

def p_const_exp(p):
    '''
    const_exp : or_expr
    '''
    p[0] = p[1]

def p_or_expr(p):
    '''
    or_expr : xor_expr
        | or_expr '|' xor_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = OrOp(p[0], p[2])

def p_xor_expr(p):
    '''
    xor_expr : and_expr
        | xor_expr TOK_CARET and_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = XorOp(p[0], p[2])

def p_and_expr(p):
    '''
    and_expr : shift_expr
        | and_expr TOK_AMPERSAND shift_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = AndOp(p[0], p[2])

def p_shift_expr(p):
    '''
    shift_expr : add_expr
        | shift_expr TOK_OP_SHR add_expr
        | shift_expr TOK_OP_SHL add_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == '>>':
            p[0] = RightShiftOp(p[0], p[2])
        else:
            p[0] = LeftShiftOp(p[0], p[2])

def p_add_expr(p):
    '''
    add_expr : mult_expr
        | add_expr '+' mult_expr
        | add_expr '-' mult_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == '+':
            p[0] = AddOp(p[0], p[2])
        else:
            p[0] = SubOp(p[0], p[2])

def p_mult_expr(p):
    '''
    mult_expr : unary_expr
        | mult_expr TOK_ASTERISK unary_expr
        | mult_expr TOK_SLASH unary_expr
        | mult_expr TOK_PERCENT unary_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == '*':
            p[0] = MulOp(p[0], p[2])
        elif [2] == '/':
            p[0] = DivOp(p[0], p[2])
        else:
            p[0] = ModOp(p[0], p[2])

def p_unary_expr(p):
    '''
    unary_expr : unary_op primary_expr
        | primary_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1](p[2])

def p_unary_op(p):
    '''
    unary_op : TOK_MINUS
        | TOK_PLUS
        | TOK_TILDE
    '''
    if p[1] == '-':
        p[0] = NegateOp
    elif p[1] == '+':
        p[0] = PlusOp
    elif p[2] == '~':
        p[0] = InvertOp

def p_primary_expr(p):
    '''
    primary_expr : scoped_name
        | literal
        | TOK_LPAREN const_exp TOK_RPAREN
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_literal(p):
    '''
    literal : integer_lit
        | string_lit
        | char_lit
        | fixed_pt_lit
        | floating_pt_lit
        | boolean_lit
    '''
    p[0] = p[1]

def p_enum_type(p):
    '''
    enum_type : modifiers_and_props TOK_ENUM z_ident_catch TOK_LBRACE enumerator_list TOK_RBRACE
    '''

def p_scoped_name(p):
    '''
    scoped_name : ident_in_current_ns
        | ident_in_specified_ns
    '''
    p[0] = p[1]

def p_ident_in_current_ns(p):
    '''
    ident_in_current_ns : scope_identifier_list
    '''
    scope = CurrentScopeNode()
    for name in p[1][0:-1]:
        scope = NamespaceReference(name=name, scope=scope)
    p[0] = SimpleTypeReferenceNode(name=p[1][-1], scope=scope)

def p_ident_in_specified_ns(p):
    '''
    ident_in_specified_ns : TOK_OP_SCOPE scope_identifier_list
    '''
    scope = NamespaceReference()
    for name in p[2][0:-1]:
        scope = NamespaceReference(name=name, scope=scope)
    p[0] = SimpleTypeReferenceNode(name=p[2][-1], scope=scope)

def p_scope_identifier_list(p):
    '''
    scope_identifier_list : ident
        | scope_identifier_list TOK_OP_SCOPE ident
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_enumerator_list(p):
    '''
    enumerator_list : ident
        | enumerator_list TOK_COMMA ident
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_struct_member_list(p):
    '''
    struct_member_list :
        | struct_member_list member
    '''
    if len(p) == 1:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_member(p):
    ''' 
    member : modifiers_and_props type_spec declarator_list TOK_SEMICOLON
    '''
    p[0] = FieldDef(type=p[2], declarators=p[3], properties=p[1][1])

def p_base_type_spec(p):
    '''
    base_type_spec : floating_pt_type
        | integer_type
        | char_type
        | wide_char_type
        | boolean_type
        | octet_type
        | any_type
        | object_type
        | typecode_type
    '''
    p[0] = p[1]

def p_template_type_spec(p):
    '''
    template_type_spec : sequence_type
        | string_type
        | wide_string_type
        | fixed_pt_type
    '''
    p[0] = p[1]

def p_sequence_type(p):
    '''
    sequence_type : TOK_SEQUENCE TOK_LT simple_type_spec TOK_COMMA positive_int_const TOK_GT
        | TOK_SEQUENCE TOK_LT simple_type_spec TOK_GT
    '''
    p[0] = SequenceType(type=p[3], size=len(p) > 5 and p[7] or None)

def p_floating_pt_type(p):
    '''
    floating_pt_type : float
        | double
        | long_double
    '''
    p[0] = p[1]

def p_float(p):
    '''
    float : TOK_FLOAT
    '''
    p[0] = BasicTypeNode(p[1])

def p_double(p):
    '''
    double : TOK_DOUBLE
    '''
    p[0] = BasicTypeNode(p[1])

def p_long_double(p):
    '''
    long_double : TOK_LONG TOK_DOUBLE
    '''
    p[0] = BasicTypeNode('long double')

def p_fixed_pt_type(p):
    '''
    fixed_pt_type : TOK_FIXED TOK_LT positive_int_const TOK_COMMA integer_lit TOK_GT
    '''
    p[0] = FixedPTypeNode(p[3], p[5])

def p_fixed_pt_const_type(p):
    '''
    fixed_pt_const_type : TOK_FIXED
    '''

def p_integer_type(p):
    '''
    integer_type : signed_int
        | unsigned_int
    '''
    p[0] = p[1]

def p_signed_int(p):
    '''
    signed_int : signed_short_int
        | signed_long_int
        | signed_longlong_int
    '''
    p[0] = p[1]

def p_signed_short_int(p):
    '''
    signed_short_int : TOK_SHORT
    '''
    p[0] = BasicTypeNode('short')

def p_signed_long_int(p):
    '''
    signed_long_int : TOK_LONG
    '''
    p[0] = BasicTypeNode('long')

def p_signed_longlong_int(p):
    '''
    signed_longlong_int : TOK_LONG TOK_LONG
    '''
    p[0] = BasicTypeNode('long long')

def p_unsigned_int(p):
    '''
    unsigned_int : unsigned_short_int
        | unsigned_long_int
        | unsigned_longlong_int
    '''
    p[0] = p[1]

def p_unsigned_short_int(p):
    '''
    unsigned_short_int : TOK_UNSIGNED TOK_SHORT
    '''
    p[0] = BasicTypeNode('unsigned short')

def p_unsigned_long_int(p):
    '''
    unsigned_long_int : TOK_UNSIGNED TOK_LONG
    '''
    p[0] = BasicTypeNode('unsigned long')

def p_unsigned_longlong_int(p):
    '''
    unsigned_longlong_int : TOK_UNSIGNED TOK_LONG TOK_LONG
    '''
    p[0] = BasicTypeNode('unsigned long long')

def p_char_type(p):
    '''
    char_type : TOK_CHAR
    '''
    p[0] = BasicTypeNode('char')

def p_wide_char_type(p):
    '''
    wide_char_type : TOK_WCHAR
    '''
    p[0] = BasicTypeNode('wchar')

def p_boolean_type(p):
    '''
    boolean_type : TOK_BOOLEAN
    '''
    p[0] = BasicTypeNode('boolean')

def p_octet_type(p):
    '''
    octet_type : TOK_OCTET
    '''

def p_any_type(p):
    '''
    any_type : TOK_ANY
    '''

def p_object_type(p):
    '''
    object_type : TOK_OBJECT
    '''

def p_typecode_type(p):
    '''
    typecode_type : TOK_TYPECODE
    '''

def p_string_type(p):
    '''
    string_type : TOK_STRING TOK_LT positive_int_const TOK_GT
        | TOK_STRING
    '''

def p_wide_string_type(p):
    '''
    wide_string_type : TOK_WSTRING TOK_LT positive_int_const TOK_GT
        | TOK_WSTRING
    '''

def p_declarator_list(p):
    '''
    declarator_list : declarator
        | declarator_list TOK_COMMA declarator
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_declarator(p):
    '''
    declarator : simple_declarator
        | complex_declarator
    '''
    p[0] = p[1]

def p_simple_declarator(p):
    '''
    simple_declarator : ident
    '''
    p[0] = p[1]

def p_complex_declarator(p):
    '''
    complex_declarator : array_declarator
    '''
    p[0] = p[1]

def p_simple_declarator_list(p):
    '''
    simple_declarator_list : simple_declarator
        | simple_declarator_list TOK_COMMA simple_declarator
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_simple_declarator_pair_list(p):
    '''
    simple_declarator_pair_list : simple_declarator_pair
        | simple_declarator_pair_list TOK_COMMA simple_declarator_pair
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_simple_declarator_pair(p):
    '''
    simple_declarator_pair : simple_declarator
        | simple_declarator TOK_EQUAL const_exp
    '''

def p_array_declarator(p):
    '''
    array_declarator : ident fixed_array_size_list
    '''
    p[0] = ArrayType(p[1], p[2])

def p_fixed_array_size_list(p):
    '''
    fixed_array_size_list : fixed_array_size
        | fixed_array_size_list fixed_array_size
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_fixed_array_size(p):
    '''
    fixed_array_size : TOK_LSQB positive_int_const TOK_RSQB
        | TOK_LSQB TOK_RSQB
    '''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = None

def p_prop_hash(p):
    '''
    prop_hash : prop_hash_elem
        | prop_hash TOK_COMMA prop_hash_elem
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]

def p_prop_hash_elem(p):
    '''
    prop_hash_elem : TOK_IDENT TOK_PROP_ARGS
        | TOK_IDENT TOK_EQUAL prop_value
        | TOK_IDENT
    '''
    if len(p) == 3:
        p[0] = Property(p[1], p[2])
    elif len(p) == 4:
        p[0] = Property(p[1], p[3])
    else:
        p[0] = Property(p[1], None)

def p_prop_value(p):
    '''
    prop_value : TOK_IDENT
        | integer_lit
        | fixed_pt_lit
        | floating_pt_lit
        | string_lit
        | char_lit
        | TOK_IDENT TOK_PROP_ARGS
    '''
    if len(p) == 3:
        p[0] = Property(p[1], p[2])
    else:
        p[0] = p[1]

def p_ident(p):
    '''
    ident : TOK_IDENT
    '''
    p[0] = Identifier(p[1])

def p_string_lit_list(p):
    '''
    string_lit_list : string_lit
        | string_lit_list TOK_COMMA string_lit
    '''

def p_positive_int_const(p):
    '''
    positive_int_const : const_exp
    '''

def p_enter_prop(p):
    '''
    enter_prop :
    '''
    p.lexer.push_state('PROP')

def p_z_props(p):
    '''
    z_props :
        | TOK_LSQB enter_prop prop_hash TOK_RSQB
    '''
    p[0] = len(p) == 5 and p[3] or []

def p_integer_lit(p):
    '''
    integer_lit : TOK_INTEGER
    '''
    p[0] = IntegerValue(p[1])

def p_string_lit(p):
    '''
    string_lit : dqstring_cat
    '''
    p[0] = StringValue(p[1])

def p_char_lit(p):
    '''
    char_lit : sqstring
    '''
    p[0] = CharValue(p[1])

def p_fixed_pt_lit(p):
    '''
    fixed_pt_lit : TOK_FIXEDP
    '''
    p[0] = FixedPValue(p[1])

def p_floating_pt_lit(p):
    '''
    floating_pt_lit : TOK_FLOATP
    '''
    p[0] = FloatValue(p[1])

def p_boolean_lit(p):
    '''
    boolean_lit : TOK_TRUE
        | TOK_FALSE
    '''
    p[0] = BooleanValue(p[1] == 'true')

def p_codefrag(p):
    '''
    codefrag : TOK_CODEFRAG
    '''

def p_dqstring_cat(p):
    '''
    dqstring_cat : dqstring
        | dqstring_cat dqstring
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Concat(p[1], p[2]) 

def p_dqstring(p):
    '''
    dqstring : TOK_DQSTRING
    '''
    p[0] = StringValue(p[1])

def p_sqstring(p):
    '''
    sqstring : TOK_SQSTRING
    '''
    p[0] = StringValue(p[2])

def p_optional_trailing_comma(p):
    '''
    optional_trailing_comma :
        | TOK_COMMA
    '''

def p_error(p):
    if p is not None:
        raise IDLSyntaxError('Syntax error', p.lexer.lineno)
    else:
        raise IDLSyntaxError('Unexpected EOF')

def raise_syntax_error(p, msg):
    raise IDLSyntaxError(msg, p.lexer.lineno)

def parser(webidl=False, **kwargs):
    retval = yacc.yacc(tabmodule='parsertab', outputdir=os.path.dirname(__file__), **kwargs)
    retval.webidl = webidl
    return retval
