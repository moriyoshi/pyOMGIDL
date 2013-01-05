import sys
from pyomgidl.reader.tree import *
from pyomgidl.reader.interfaces import INodeVisitor
from zope.interface import implements

__all__ = [
    'InterfaceGenerator',
    ]

def render_value(value_node):
    if isinstance(value_node, (IntegerValue, FloatValue)):
        return value_node.value
    elif isinstance(value_node, StringValue):
        return repr(value_node.value)
    elif isinstance(value_node, BooleanValue):
        return repr(value_node.value)
    else:
        raise Exception("Unsupported type")

class InterfaceGenerator(object):
    implements(INodeVisitor)

    def __init__(self, base_dir, prefix=None, out=sys.stdout, shifter='    '):
        self.base_dir = base_dir
        self.prefix = prefix
        self.module_stack = []
        self.out = out
        self.shifter = shifter
        self.pad = ''
        if prefix:
            self.module_stack.append(prefix)

    def current_module(self):
        return sum((i.split('.') for i in self.module_stack), [])

    def resolve_type(self, node):
        scope_ref = []
        if isinstance(node, SimpleTypeReferenceNode):
            if node.scope.__class__ != CurrentScopeNode:
                scope_ref = resolve_scope(node.scope)
            return (scope_ref and '.'.join(scope_ref) + '.' or '') + node.name.value
        elif isinstance(node, BasicTypeNode):
            return node.name
        raise Exception('Oops: %s' % node)

    def resolve_scope(self, node):
        retval = []
        def _(node):
            retval.append(node.name) 
            if node.scope is not None:
                _(node.scope)
        _(node)
        return retval

    def indent(self):
        self.pad += self.shifter

    def dedent(self):
        self.pad = self.pad[0:-len(self.shifter)]

    def write(self, line=''):
        self.out.write(self.pad)
        self.out.write(line)
        self.out.write("\n")

    def visit_specification(self, node):
        self.write('import zope.interface')
        self.write()

    def depart_specification(self, node):
        pass

    def visit_module(self, node):
        self.module_stack.append(node.name.value)

    def depart_module(self, node):
        self.module_stack.pop()

    def visit_interface(self, node):
        if node.body is not None:
            supers = node.supers and (self.resolve_type(super) for super in node.supers) or ['zope.interface.Interface']
            self.write("class %s(%s):" % (node.name.value, ', '.join(supers)))
            self.indent()

    def depart_interface(self, node):
        if node.body is not None:
            self.dedent()

    def visit_value_type(self, node):
        pass

    def depart_value_type(self, node):
        pass

    def visit_struct(self, node):
        pass

    def depart_struct(self, node):
        pass

    def visit_enum(self, node):
        pass

    def depart_enum(self, node):
        pass

    def visit_union(self, node):
        pass

    def depart_union(self, node):
        pass

    def visit_type_def(self, node):
        pass

    def visit_native_decl(self, node):
        pass

    def visit_attr_def(self, node):
        for declarator in node.declarators:
            doc = ''
            if node.readonly:
                doc += '[readonly] '
            doc += self.resolve_type(node.type)
            self.write("%s = zope.interface.Attribute('''%s''')" % (declarator.identifier.value, doc))
            self.write()

    def visit_operation_def(self, node):
        def gen_arg(item):
            if item.default_value is not None:
                return "%s = %s" % (item.name.value, render_value(item.default_value))
            else:
                return item.name.value
        self.write("def %s(%s):" % (node.name.value, ", ".join(gen_arg(item) for item in node.parameters.items)))
        self.indent()
        self.write("pass")
        self.dedent()
        self.write()

    def visit_field_def(self, node):
        pass

    def visit_const_decl(self, node):
        pass

    def __call__(self, spec):
        walk_ast_nodes(spec, self)

