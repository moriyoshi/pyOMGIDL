import sys
from zope.interface.verify import verifyObject
from pyomgidl.reader.interfaces import INodeVisitor

class ASTNode(object):
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join('%s=%r' % (k, getattr(self, k)) for k in dir(self) if not k.startswith('__')))

class LeafASTNode(ASTNode):
    pass

class ValueNode(LeafASTNode):
    def __init__(self, value):
        self.value = value

    def __eq__(self, that):
        return isinstance(that, self.__class__) and self.value == that.value

class Definition(ASTNode):
    pass

class DefinitionContainer(Definition):
    def __init__(self, definitions=[]):
        self.definitions = definitions

    def __eq__(self, that):
        return isinstance(that, DefinitionContainer) and \
               self.definitions == that.definitions

class Specification(DefinitionContainer):
    pass

class Module(DefinitionContainer):
    def __init__(self, definitions=[], name=None):
        super(Module, self).__init__(definitions)
        self.name = name

    def __eq__(self, that):
        return isinstance(that, Module) and \
               self.definitions == that.definitions and \
               self.name == that.name

class Interface(Definition):
    def __init__(self, name, properties=[], supers=None, body=None):
        self.properties = properties
        self.name = name
        self.supers = supers
        self.body = body

    def __eq__(self, that):
        return isinstance(that, Interface) and \
               self.properties == that.properties and \
               self.name == that.name and \
               self.supers == that.supers and \
               self.body == that.body

class ValueType(Definition):
    def __init__(self, name, properties=[], super=None, body=None):
        self.properties = properties
        self.name = name
        self.super = super
        self.body = body

    def __eq__(self, that):
        return isinstance(that, Definition) and \
               self.properties == that.properties and \
               self.name == that.name and \
               self.super == that.super and \
               self.body == that.body

class Struct(Definition):
    pass

class Enum(Definition):
    pass

class Union(Definition):
    pass

class Identifier(ValueNode):
    pass

class Property(LeafASTNode):
    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    def __eq__(self, that):
        return isinstance(that, Property) and \
               self.key == that.key and \
               self.value == that.value

class TypeDef(Definition):
    def __init__(self, type, declarators, properties=[]):
        self.type = type
        self.declarators = declarators
        self.properties = properties

    def __eq__(self, that):
        return isinstance(that, TypeDef) and \
               self.type == that.type and \
               self.declarators == that.declarators and \
               self.properties == that.properties

class NativeDecl(Definition):
    def __init__(self, declarator, native_type=None, properties=[]):
        self.declarator = declarator
        self.native_type = native_type
        self.properties = properties

    def __eq__(self, that):
        return isinstance(that, NativeDecl) and \
               self.native_type == that.native_type and \
               self.declarator == that.declarator and \
               self.properties == that.properties

class ExceptionDecl(Definition):
    def __init__(self, name, members=[], properties=[]):
        self.name = name
        self.members = members
        self.properties = properties

    def __eq__(self, that):
        return isinstance(that, ExceptionDecl) and \
               self.name == that.name and \
               self.members == that.members and \
               self.properties == that.properties

class ConstDecl(Definition):
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value

    def __eq__(self, that):
        return isinstance(that, ConstDecl) and \
               self.name == that.name and \
               self.type == that.type and \
               self.value == that.value

class StringValue(ValueNode):
    pass

class CharValue(ValueNode):
    pass

class IntegerValue(ValueNode):
    pass

class FloatValue(ValueNode):
    pass

class FixedPValue(ValueNode):
    pass

class BooleanValue(ValueNode):
    pass

class TypeNode(ASTNode):
    pass

class ScopeNode(LeafASTNode):
    pass

class CurrentScopeNode(ScopeNode):
    def __eq__(self, that):
        return isinstance(that, CurrentScopeNode)

class NamespaceReference(ScopeNode):
    def __init__(self, name=None, scope=None):
        self.name = name
        self.scope = scope
    
    def __eq__(self, that):
        return isinstance(that, ScopeNode) and \
               self.name == that.name and \
               self.scope == that.scope

class SimpleTypeReferenceNode(TypeNode):
    def __init__(self, name, scope=None):
        self.name = name
        self.scope = scope

    def __eq__(self, that):
        return isinstance(that, SimpleTypeReferenceNode) and \
               self.name == that.name and self.scope == that.scope

class BasicTypeNode(TypeNode):
    def __init__(self, name):
        self.name = name

    def __eq__(self, that):
        return isinstance(that, BasicTypeNode) and \
               self.name == that.name

class FixedPTypeNode(TypeNode):
    def __init__(self, precision, scale):
        self.precision = precision
        self.scale = scale

    def __eq__(self, that):
        return isinstance(that, FixedPTypeNode) and \
               self.precision == that.precision and \
               self.scale == that.scale

class CompoundTypeNode(TypeNode):
    pass

class ArrayType(CompoundTypeNode):
    def __init__(self, type, dimension):
        self.type = type
        self.dimension = dimension

    def __eq__(self, that):
        return isinstance(that, ArrayType) and \
            self.type == that.type and \
            self.dimension == that.dimension

class SequenceType(CompoundTypeNode):
    def __init__(self, type, size):
        self.type = type
        self.size = size

    def __eq__(self, that):
        return isinstance(that, SequenceType) and \
            self.type == that.type and \
            self.size == that.size

class Concat(ASTNode):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __eq__(self, that):
        return isinstance(that, self.__class__) and \
            self.lhs == that.lhs and \
            self.rhs == that.rhs

class BinaryOpNode(ASTNode):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __eq__(self, that):
        return isinstance(that, self.__class__) and \
            self.lhs == that.lhs and \
            self.rhs == that.rhs

class OrOp(BinaryOpNode):
    pass

class XorOp(BinaryOpNode):
    pass

class AndOp(BinaryOpNode):
    pass

class LeftShiftOp(BinaryOpNode):
    pass

class RightShiftOp(BinaryOpNode):
    pass

class AddOp(BinaryOpNode):
    pass

class SubOp(BinaryOpNode):
    pass

class MulOp(BinaryOpNode):
    pass

class DivOp(BinaryOpNode):
    pass

class ModOp(BinaryOpNode):
    pass

class UnaryOpNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def __eq__(self, that):
        return isinstance(that, self.__class__) and \
            self.lhs == that.expr

class NegateOp(UnaryOpNode):
    pass

class PlusOp(UnaryOpNode):
    pass

class InvertOp(UnaryOpNode):
    pass

class Member(Definition):
    pass

class AttrDef(Member):
    def __init__(self, type, readonly, nullable, declarators, properties):
        self.type = type
        self.readonly = readonly
        self.nullable = nullable
        self.declarators = declarators
        self.properties = properties

    def __eq__(self, that):
        return isinstance(that, AttrDef) and \
               self.type == that.type and \
               self.readonly == that.readonly and \
               self.declarators == that.declarators and \
               self.properties == that.properties

class FieldDef(Member):
    def __init__(self, type, declarators, properties):
        self.type = type
        self.declarators = declarators
        self.properties = properties

    def __eq__(self, that):
        return isinstance(that, FieldDef) and \
               self.type == that.type and \
               self.declarators == that.declarators and \
               self.properties == that.properties

class OperationDef(Member):
    def __init__(self, name, return_type, parameters, raises, oneway, context, properties=[]):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters
        self.raises = raises
        self.oneway = oneway
        self.context = context
        self.properties = properties

    def __eq__(self, that):
        return isinstance(that, OperationDef) and \
               self.name == that.name and \
               self.return_type == that.return_type and \
               self.parameters == that.parameters and \
               self.raises == that.raises and \
               self.oneway == that.oneway and \
               self.context == that.context and \
               self.properties == that.properties

class Parameters(ASTNode):
    def __init__(self, items, varargs=False):
        self.items = items
        self.varargs = varargs

    def __eq__(self, that):
        return isinstance(that, Parameters) and \
               self.items == that.items and \
               self.varargs == that.varargs

class Parameter(ASTNode):
    def __init__(self, name, type, nullable, direction, default_value, properties=[]):
        self.name = name
        self.type = type
        self.nullable = nullable
        self.direction = direction
        self.default_value = default_value
        self.properties = properties

    def __eq__(self, that):
        return isinstance(that, Parameter) and \
            self.name == that.name and \
            self.type == that.type and \
            self.direction == that.direction and \
            self.default_value == that.default_value and \
            self.properties == that.properties

def is_non_string_iterable(value):
    return not isinstance(value, basestring) and hasattr(value, '__iter__')

def walk_ast_nodes(node, visitor):
    verifyObject(INodeVisitor, visitor)
    depart = None
    if isinstance(node, Specification):
        visitor.visit_specification(node)
        depart = visitor.depart_specification
    elif isinstance(node, Module):
        visitor.visit_module(node)
        depart = visitor.depart_module
    elif isinstance(node, Interface):
        visitor.visit_interface(node)
        depart = visitor.depart_interface
    elif isinstance(node, ValueType):
        visitor.visit_value_type(node)
        depart = visitor.depart_value_type
    elif isinstance(node, TypeDef):
        visitor.visit_type_def(node)
    elif isinstance(node, NativeDecl):
        visitor.visit_native_decl(node)
    elif isinstance(node, Struct):
        visitor.visit_struct(node)
        depart = visitor.depart_struct
    elif isinstance(node, Enum):
        visitor.visit_enum(node)
        depart = visitor.depart_enum
    elif isinstance(node, Union):
        visitor.visit_union(node)
        depart = visitor.depart_union
    elif isinstance(node, AttrDef):
        visitor.visit_attr_def(node)
    elif isinstance(node, OperationDef):
        visitor.visit_operation_def(node)
    elif isinstance(node, FieldDef):
        visitor.visit_field_def(node)
    elif isinstance(node, ConstDecl):
        visitor.visit_const_decl(node)

    if isinstance(node, DefinitionContainer):
        for definition in node.definitions:
            walk_ast_nodes(definition, visitor)
    elif isinstance(node, Interface):
        if node.body is not None:
            for member in node.body:
                walk_ast_nodes(member, visitor)
    elif isinstance(node, ValueType):
        if node.body is not None:
            for member in node.body:
                walk_ast_nodes(member, visitor)
    elif isinstance(node, Struct):
        for member in node.body:
            walk_ast_nodes(member, visitor)
    elif isinstance(node, Enum):
        for member in node.body:
            walk_ast_nodes(member, visitor)
    elif isinstance(node, Union):
        for member in node.body:
            walk_ast_nodes(member, visitor)
        

    if depart is not None:
        depart(node)

class PrettyPrinter(object):
    def __init__(self, out, shifter='  '):
        self.out = out
        self.shifter = shifter
        self.pad = ''

    def indent(self):
        self.pad += self.shifter

    def dedent(self):
        self.pad = self.pad[0:-len(self.shifter)]

    def render_dict(self, value):
        if len(value) == 0:
            self.out.write("{}")
        else:
            self.out.write("{\n")
            self.indent()
            for k, v in value.iteritems():
                self.out.write("%s%r:" % (self.pad, k))
                self.render(v)
                self.out.write(",\n")
            self.out.write("%s}\n" % self.pad)
            self.dedent()

    def render_list(self, value):
        if len(value) == 0:
            self.out.write("[]")
        else:
            self.out.write("[\n")
            self.indent()
            for v in value:
                self.render(v)
                self.out.write(",\n")
            self.out.write("%s]" % self.pad)
            self.dedent()

    def _render(self, node):
        if isinstance(node, ValueNode):
            self.out.write("%s(%r)" % (node.__class__.__name__, node.value))
        elif isinstance(node, ASTNode):
            self.out.write("%s(\n" % (node.__class__.__name__))
            self.indent()
            attr_names = [attr_name for attr_name in dir(node) if not attr_name.startswith('__')]
            def _(a, b):
                a_value = getattr(node, a)
                b_value = getattr(node, b)
                a_is_iterable = is_non_string_iterable(a_value)
                b_is_iterable = is_non_string_iterable(b_value)
                if a_is_iterable:
                    if b_is_iterable:
                        return cmp(a, b)
                    else:
                        return 1
                else:
                    if b_is_iterable:
                        return -1
                    else:
                        return cmp(a, b)
            attr_names.sort(_)
            for attr_name in attr_names:
                attr_value = getattr(node, attr_name)
                self.out.write("%s%s=" % (self.pad, attr_name))
                if isinstance(attr_value, dict):
                    self.render_dict(attr_value)
                elif is_non_string_iterable(attr_value):
                    self.render_list(attr_value)
                else:
                    self.out.write("%r" % attr_value)
                self.out.write(",\n")
            self.out.write("%s)" % self.pad)
            self.dedent()
        else:
            self.out.write("%r" % node)

    def render(self, node):
        self.out.write(self.pad)
        self._render(node)

def pp(node, out=sys.stdout, shifter='  '):
    PrettyPrinter(out, shifter).render(node)
    out.flush()

