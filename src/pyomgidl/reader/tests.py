from unittest import TestCase
from pyomgidl.reader import lexer, parser, tree, IDLSyntaxError

class TokenizerTest(TestCase):
    def setUp(self):
        self.lex = lexer()

    def tearDown(self):
        pass

    def assertToken(self, type_value_pair, lineno=None):
        token = self.lex.token()
        self.assertEqual(type_value_pair[0], token.type) 
        self.assertEqual(type_value_pair[1], token.value)
        if lineno is not None:
            self.assertEqual(lineno, token.lineno)

    def assertEof(self):
        self.assertEqual(None, self.lex.token())

    def input(self, value):
        self.lex.input(value)

    def testTokenizerColon(self):
        self.input(':')
        self.assertToken(('TOK_COLON', ':'))
        self.assertEof()

    def testTokenizerSemicolon(self):
        self.input(';')
        self.assertToken(('TOK_SEMICOLON', ';'))
        self.assertEof()

    def testTokenizerBraces(self):
        self.input('{')
        self.assertToken(('TOK_LBRACE', '{'))
        self.assertEof()
        self.input('}')
        self.assertToken(('TOK_RBRACE', '}'))
        self.assertEof()

    def testTokenizerParentheses(self):
        self.input('(')
        self.assertToken(('TOK_LPAREN', '('))
        self.assertEof()
        self.input(')')
        self.assertToken(('TOK_RPAREN', ')'))
        self.assertEof()

    def testTokenizerCaret(self):
        self.input('^')
        self.assertToken(('TOK_CARET', '^'))
        self.assertEof()

    def testTokenizerAmpersand(self):
        self.input('&')
        self.assertToken(('TOK_AMPERSAND', '&'))
        self.assertEof()

    def testTokenizerPlus(self):
        self.input('+')
        self.assertToken(('TOK_PLUS', '+'))
        self.assertEof()

    def testTokenizerMinus(self):
        self.input('-')
        self.assertToken(('TOK_MINUS', '-'))
        self.assertEof()

    def testTokenizerAsterisk(self):
        self.input('*')
        self.assertToken(('TOK_ASTERISK', '*'))
        self.assertEof()

    def testTokenizerSlash(self):
        self.input('/')
        self.assertToken(('TOK_SLASH', '/'))
        self.assertEof()

    def testTokenizerPercent(self):
        self.input('%')
        self.assertToken(('TOK_PERCENT', '%'))
        self.assertEof()

    def testTokenizerTilde(self):
        self.input('~')
        self.assertToken(('TOK_TILDE', '~'))
        self.assertEof()

    def testTokenizerLsqb(self):
        self.input('[')
        self.assertToken(('TOK_LSQB', '['))
        self.assertEof()

    def testTokenizerRsqb(self):
        self.input(']')
        self.assertToken(('TOK_RSQB', ']'))
        self.assertEof()

    def testTokenizerLt(self):
        self.input('<')
        self.assertToken(('TOK_LT', '<'))
        self.assertEof()

    def testTokenizerGt(self):
        self.input('>')
        self.assertToken(('TOK_GT', '>'))
        self.assertEof()

    def testTokenizerAny(self):
        self.input('any')
        self.assertToken(('TOK_ANY', 'any'))
        self.assertEof()

    def testTokenizerAttribute(self):
        self.input('attribute')
        self.assertToken(('TOK_ATTRIBUTE', 'attribute'))
        self.assertEof()

    def testTokenizerBoolean(self):
        self.input('boolean')
        self.assertToken(('TOK_BOOLEAN', 'boolean'))
        self.assertEof()

    def testTokenizerCase(self):
        self.input('case')
        self.assertToken(('TOK_CASE', 'case'))
        self.assertEof()

    def testTokenizerChar(self):
        self.input('char')
        self.assertToken(('TOK_CHAR', 'char'))
        self.assertEof()

    def testTokenizerConst(self):
        self.input('const')
        self.assertToken(('TOK_CONST', 'const'))
        self.assertEof()

    def testTokenizerContext(self):
        self.input('context')
        self.assertToken(('TOK_CONTEXT', 'context'))
        self.assertEof()

    def testTokenizerDefault(self):
        self.input('default')
        self.assertToken(('TOK_DEFAULT', 'default'))
        self.assertEof()

    def testTokenizerDouble(self):
        self.input('double')
        self.assertToken(('TOK_DOUBLE', 'double'))
        self.assertEof()

    def testTokenizerEnum(self):
        self.input('enum')
        self.assertToken(('TOK_ENUM', 'enum'))
        self.assertEof()

    def testTokenizerException(self):
        self.input('exception')
        self.assertToken(('TOK_EXCEPTION', 'exception'))
        self.assertEof()

    def testTokenizerFalse(self):
        self.input('false')
        self.assertToken(('TOK_FALSE', 'false'))
        self.assertEof()

    def testTokenizerFixed(self):
        self.input('fixed')
        self.assertToken(('TOK_FIXED', 'fixed'))
        self.assertEof()

    def testTokenizerIn(self):
        self.input('in')
        self.assertToken(('TOK_IN', 'in'))
        self.assertEof()

    def testTokenizerInout(self):
        self.input('inout')
        self.assertToken(('TOK_INOUT', 'inout'))
        self.assertEof()

    def testTokenizerInterface(self):
        self.input('interface')
        self.assertToken(('TOK_INTERFACE', 'interface'))
        self.assertEof()

    def testTokenizerLong(self):
        self.input('long')
        self.assertToken(('TOK_LONG', 'long'))
        self.assertEof()

    def testTokenizerModule(self):
        self.input('module')
        self.assertToken(('TOK_MODULE', 'module'))
        self.assertEof()

    def testTokenizerNative(self):
        self.input('native(a);')
        self.assertToken(('TOK_NATIVE', 'native'))
        self.assertEqual('NATIVE', self.lex.lexstate)
        self.assertToken(('TOK_LPAREN', '('))
        self.assertEqual('NATIVETYPE', self.lex.lexstate)
        self.assertToken(('TOK_NATIVE_TYPE', 'a'))
        self.assertEqual('NATIVETYPE', self.lex.lexstate)
        self.assertToken(('TOK_RPAREN', ')'))
        self.assertEqual('INITIAL', self.lex.lexstate)
        self.assertToken(('TOK_SEMICOLON', ';'))
        self.assertEqual('INITIAL', self.lex.lexstate)
        self.assertEof()

    def testTokenizerObject(self):
        self.input('object')
        self.assertToken(('TOK_OBJECT', 'object'))
        self.assertEof()
        self.input('Object')
        self.assertToken(('TOK_OBJECT', 'Object'))
        self.assertEof()

    def testTokenizerOctet(self):
        self.input('octet')
        self.assertToken(('TOK_OCTET', 'octet'))
        self.assertEof()

    def testTokenizerOneway(self):
        self.input('oneway')
        self.assertToken(('TOK_ONEWAY', 'oneway'))
        self.assertEof()

    def testTokenizerScopeOp(self):
        self.input('::')
        self.assertToken(('TOK_OP_SCOPE', '::'))
        self.assertEof()

    def testTokenizerShlOp(self):
        self.input('<<')
        self.assertToken(('TOK_OP_SHL', '<<'))
        self.assertEof()

    def testTokenizerShrOp(self):
        self.input('>>')
        self.assertToken(('TOK_OP_SHR', '>>'))
        self.assertEof()

    def testTokenizerOut(self):
        self.input('out')
        self.assertToken(('TOK_OUT', 'out'))
        self.assertEof()

    def testTokenizerRaises(self):
        self.input('raises')
        self.assertToken(('TOK_RAISES', 'raises'))
        self.assertEof()

    def testTokenizerReadonly(self):
        self.input('readonly')
        self.assertToken(('TOK_READONLY', 'readonly'))
        self.assertEof()

    def testTokenizerSequence(self):
        self.input('sequence')
        self.assertToken(('TOK_SEQUENCE', 'sequence'))
        self.assertEof()

    def testTokenizerShort(self):
        self.input('short')
        self.assertToken(('TOK_SHORT', 'short'))
        self.assertEof()

    def testTokenizerString(self):
        self.input('string')
        self.assertToken(('TOK_STRING', 'string'))
        self.assertEof()

    def testTokenizerStruct(self):
        self.input('struct')
        self.assertToken(('TOK_STRUCT', 'struct'))
        self.assertEof()

    def testTokenizerSwitch(self):
        self.input('switch')
        self.assertToken(('TOK_SWITCH', 'switch'))
        self.assertEof()

    def testTokenizerTrue(self):
        self.input('true')
        self.assertToken(('TOK_TRUE', 'true'))
        self.assertEof()

    def testTokenizerTypecode(self):
        self.input('typecode')
        self.assertToken(('TOK_TYPECODE', 'typecode'))
        self.assertEof()
        self.input('TypeCode')
        self.assertToken(('TOK_TYPECODE', 'TypeCode'))
        self.assertEof()

    def testTokenizerTypedef(self):
        self.input('typedef')
        self.assertToken(('TOK_TYPEDEF', 'typedef'))
        self.assertEof()

    def testTokenizerValuetype(self):
        self.input('valuetype')
        self.assertToken(('TOK_VALUETYPE', 'valuetype'))
        self.assertEof()

    def testTokenizerUnion(self):
        self.input('union')
        self.assertToken(('TOK_UNION', 'union'))
        self.assertEof()

    def testTokenizerUnsigned(self):
        self.input('unsigned')
        self.assertToken(('TOK_UNSIGNED', 'unsigned'))
        self.assertEof()

    def testTokenizerVarargs(self):
        self.input('varargs')
        self.assertToken(('TOK_VARARGS', 'varargs'))
        self.assertEof()

    def testTokenizerVoid(self):
        self.input('void')
        self.assertToken(('TOK_VOID', 'void'))
        self.assertEof()

    def testTokenizerWchar(self):
        self.input('wchar')
        self.assertToken(('TOK_WCHAR', 'wchar'))
        self.assertEof()

    def testTokenizerWstring(self):
        self.input('wstring')
        self.assertToken(('TOK_WSTRING', 'wstring'))
        self.assertEof()

    def testTokenizerFloatp(self):
        self.input('0.5')
        self.assertToken(('TOK_FLOATP', '0.5'))
        self.assertEof()
        self.input('.5')
        self.assertToken(('TOK_FLOATP', '.5'))
        self.assertEof()
        self.input('0.15')
        self.assertToken(('TOK_FLOATP', '0.15'))
        self.assertEof()
        self.input('.15')
        self.assertToken(('TOK_FLOATP', '.15'))
        self.assertEof()
        self.input('0.5e0')
        self.assertToken(('TOK_FLOATP', '0.5e0'))
        self.assertEof()
        self.input('.5e0')
        self.assertToken(('TOK_FLOATP', '.5e0'))
        self.assertEof()
        self.input('.15e0')
        self.assertToken(('TOK_FLOATP', '.15e0'))
        self.assertEof()
        self.input('0.15e0')
        self.assertToken(('TOK_FLOATP', '0.15e0'))
        self.assertEof()
        self.input('0.5E0')
        self.assertToken(('TOK_FLOATP', '0.5E0'))
        self.assertEof()
        self.input('.5E0')
        self.assertToken(('TOK_FLOATP', '.5E0'))
        self.assertEof()
        self.input('.15E0')
        self.assertToken(('TOK_FLOATP', '.15E0'))
        self.assertEof()
        self.input('0.15E0')
        self.assertToken(('TOK_FLOATP', '0.15E0'))
        self.assertEof()
        self.input('0.5e-1')
        self.assertToken(('TOK_FLOATP', '0.5e-1'))
        self.assertEof()
        self.input('.5e-1')
        self.assertToken(('TOK_FLOATP', '.5e-1'))
        self.assertEof()
        self.input('.15e-1')
        self.assertToken(('TOK_FLOATP', '.15e-1'))
        self.assertEof()
        self.input('0.15e-1')
        self.assertToken(('TOK_FLOATP', '0.15e-1'))
        self.assertEof()
        self.input('0.5E-1')
        self.assertToken(('TOK_FLOATP', '0.5E-1'))
        self.assertEof()
        self.input('.5E-1')
        self.assertToken(('TOK_FLOATP', '.5E-1'))
        self.assertEof()
        self.input('.15E-1')
        self.assertToken(('TOK_FLOATP', '.15E-1'))
        self.assertEof()
        self.input('0.15E-1')
        self.assertToken(('TOK_FLOATP', '0.15E-1'))
        self.assertEof()

    def testTokenizerInteger(self):
        self.input('0')
        self.assertToken(('TOK_INTEGER', '0'))
        self.assertEof()
        self.input('123')
        self.assertToken(('TOK_INTEGER', '123'))
        self.assertEof()
        self.input('012')
        self.assertToken(('TOK_INTEGER', '012'))
        self.assertEof()
        self.input('0x14')
        self.assertToken(('TOK_INTEGER', '0x14'))
        self.assertEof()

    def testTokenizerProp_key(self):
        self.lex.push_state('PROP')
        self.input('(value)')
        self.assertToken(('TOK_PROP_VALUE', '(value)'))
        self.assertEof()

    def testTokenizerProp_value(self):
        self.lex.push_state('PROP')
        self.input('(aaa)')
        self.assertToken(('TOK_PROP_VALUE', '(aaa)'))
        self.assertEof()

    def testTokenizerSqstring(self):
        self.input("''")
        self.assertToken(('TOK_SQSTRING', "''"))
        self.assertEof()
        self.input("'test'")
        self.assertToken(('TOK_SQSTRING', "'test'"))
        self.assertEof()

    def testTokenizerDqstring(self):
        self.input('""')
        self.assertToken(('TOK_DQSTRING', '""'))
        self.input('"test"')
        self.assertToken(('TOK_DQSTRING', '"test"'))
        self.assertEof()

    def testTokenizerFixedp(self):
        self.input('.5d')
        self.assertToken(('TOK_FIXEDP', '.5d'))
        self.assertEof()
        self.input('.5D')
        self.assertToken(('TOK_FIXEDP', '.5D'))
        self.assertEof()
        self.input('0.5d')
        self.assertToken(('TOK_FIXEDP', '0.5d'))
        self.assertEof()
        self.input('0.5D')
        self.assertToken(('TOK_FIXEDP', '0.5D'))
        self.assertEof()

    def testTokenizerIdentifier(self):
        self.input('test')
        self.assertToken(('TOK_IDENT', 'test'))
        self.assertEof()

    def testSrcFileDirective(self):
        self.input("# 123\nx")
        self.assertToken(('TOK_IDENT', 'x'), 123)
        self.assertEof()
        self.input("# 123 aaa\nx")
        self.assertToken(('TOK_IDENT', 'x'), 123)
        self.assertEof()
        self.input("#line 123\nx")
        self.assertToken(('TOK_IDENT', 'x'), 123)
        self.assertEof()
        self.input("#line 123 aaa\nx")
        self.assertToken(('TOK_IDENT', 'x'), 123)
        self.assertEof()
        self.input("# line 123\nx")
        self.assertToken(('TOK_IDENT', 'x'), 123)
        self.assertEof()
        self.input("# line 123 aaa\nx")
        self.assertToken(('TOK_IDENT', 'x'), 123)
        self.assertEof()

    def testPragmaDirective(self):
        self.input("#pragma aaa\n#pragma bbb\nx")
        self.assertToken(('TOK_IDENT', 'x'))
        self.assertTrue('aaa' in self.lex.pragma)
        self.assertTrue('bbb' in self.lex.pragma)
        self.assertEof()
        self.input("#pragma aaa ccc\n#pragma bbb ddd\nx")
        self.assertToken(('TOK_IDENT', 'x'))
        self.assertTrue('ccc', self.lex.pragma['aaa'])
        self.assertTrue('ddd', self.lex.pragma['bbb'])
        self.assertEof()
        self.input("# pragma aaa\n# pragma bbb\nx")
        self.assertToken(('TOK_IDENT', 'x'))
        self.assertTrue('aaa' in self.lex.pragma)
        self.assertTrue('bbb' in self.lex.pragma)
        self.assertEof()
        self.input("# line 1\n# pragma aaa\n# pragma bbb\nx")
        self.assertToken(('TOK_IDENT', 'x'))
        self.assertTrue('aaa' in self.lex.pragma)
        self.assertTrue('bbb' in self.lex.pragma)
        self.assertEof()

    def testOnelinerComment(self):
        self.input("// test1\n")
        self.input("// test2\r")
        self.input("// test3\r\n")
        self.input("&")
        self.assertToken(('TOK_AMPERSAND', '&'))
        self.assertEof()

    def testBlockComment(self):
        self.input("/* test */\r\n/* test\ntest\ntest */\r\n")
        self.input("&")
        self.assertToken(('TOK_AMPERSAND', '&'))
        self.assertEof()

class ParserTest(TestCase):
    def setUp(self):
        self.parser = parser(debug=True)

    def parse(self, text):
        return self.parser.parse(text, lexer=lexer())

    def tearDown(self):
        pass

    def testSpeficiation(self):
        self.assertIsInstance(self.parse(''), tree.Specification)

    def testInterfaceBasic(self):
        self.assertEqual(
            tree.Interface(name=tree.Identifier('abc')),
            self.parse('''interface abc {};''').definitions[0])
        self.assertEqual(
            tree.Interface(name=tree.Identifier('abc'), properties=[tree.Property('prop')]),
            self.parse('''[prop] interface abc {};''').definitions[0])

    def testInterfaceReserved(self):
        try:
            self.parse('''interface Object {};''')
            self.fail('Exception has not been raised')
        except IDLSyntaxError:
            self.assertTrue(True)

        try:
            self.parse('''interface TypeCode {};''')
            self.fail('Exception has not been raised')
        except IDLSyntaxError:
            self.assertTrue(True)

    def testTypedefs(self):
        self.assertEqual(
            tree.TypeDef(
                declarators=[tree.Identifier('bar')],
                properties=[],
                type=tree.SimpleTypeReferenceNode(
                    name=tree.Identifier('foo'),
                    scope=tree.CurrentScopeNode())
                ),
            self.parse('''typedef foo bar;''').definitions[0])
        self.assertEqual(
            tree.TypeDef(
                declarators=[tree.Identifier('bar')],
                properties=[],
                type=tree.SimpleTypeReferenceNode(
                    name=tree.Identifier('foo'),
                    scope=tree.NamespaceReference(
                        tree.Identifier('ns'),
                        tree.CurrentScopeNode()))
                ),
            self.parse('''typedef ns::foo bar;''').definitions[0])
        self.assertEqual(
            tree.TypeDef(
                declarators=[tree.Identifier('bar')],
                properties=[],
                type=tree.SimpleTypeReferenceNode(
                    name=tree.Identifier('foo'),
                    scope=tree.NamespaceReference())
                ),
            self.parse('''typedef ::foo bar;''').definitions[0])
        self.assertEqual(
            tree.TypeDef(
                declarators=[tree.Identifier('bar')],
                properties=[],
                type=tree.SimpleTypeReferenceNode(
                    name=tree.Identifier('foo'),
                    scope=tree.NamespaceReference(
                        tree.Identifier('ns'),
                        tree.NamespaceReference()))
                ),
            self.parse('''typedef ::ns::foo bar;''').definitions[0])
        self.assertEqual(
            tree.TypeDef(
                declarators=[tree.Identifier('bar')],
                properties=[tree.Property('prop')],
                type=tree.SimpleTypeReferenceNode(
                    name=tree.Identifier('foo'),
                    scope=tree.CurrentScopeNode())),
            self.parse('''[prop] typedef foo bar;''').definitions[0])
        self.assertEqual(
            tree.TypeDef(
                declarators=[tree.Identifier('bar'), tree.Identifier('baz')],
                properties=[],
                type=tree.SimpleTypeReferenceNode(
                    name=tree.Identifier('foo'),
                    scope=tree.CurrentScopeNode())),
            self.parse('''typedef foo bar, baz;''').definitions[0])

    def testNative(self):
        self.assertEqual(
            tree.NativeDecl(
                declarator=tree.Identifier('NativeType'),
                native_type=None,
                properties=[]),
            self.parse('''native NativeType;''').definitions[0])
        self.assertEqual(
            tree.NativeDecl(
                declarator=tree.Identifier('NativeType'),
                native_type='something native',
                properties=[]),
            self.parse('''native NativeType(something native);''').definitions[0])
        self.assertEqual(
            tree.NativeDecl(
                declarator=tree.Identifier('NativeType'),
                properties=[tree.Property('prop')]),
            self.parse('''[prop] native NativeType;''').definitions[0])

