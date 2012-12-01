from zope.interface import Interface

class INodeVisitor(Interface):
    def visit_specification(node):
        pass

    def depart_specification(node):
        pass

    def visit_module(node):
        pass

    def depart_module(node):
        pass

    def visit_interface(node):
        pass

    def depart_interface(node):
        pass

    def visit_value_type(node):
        pass

    def depart_value_type(node):
        pass

    def visit_struct(node):
        pass

    def depart_struct(node):
        pass

    def visit_enum(node):
        pass

    def depart_enum(node):
        pass

    def visit_union(node):
        pass

    def depart_union(node):
        pass

    def visit_type_def(node):
        pass

    def visit_native_decl(node):
        pass

    def visit_attr_def(node):
        pass

    def visit_operation_def(node):
        pass

    def visit_field_def(node):
        pass

