import ply.cpp
import ply.lex
import re

__all__ = [
    'preprocess',
    'tokenize',
    ]

ESCAPE_TABLE = {
    u"\a": u"\\a",
    u"\b": u"\\b",
    u"\f": u"\\f",
    u"\n": u"\\n",
    u"\r": u"\\r",
    u"\t": u"\\t",
    u"\v": u"\\v",
    }

def litescape(s):
    def escape_char(c):
        retval = ESCAPE_TABLE.get(c)
        if retval is not None:
            return retval
        return u"\\u%04x" % ord(c)

    return re.sub(ur"[\x00-\x1f\\\xff]", lambda m: escape_Char(m.groups(0)), s)

class CustomizedPreprocessor(ply.cpp.Preprocessor):
    def parsegen(self,input,source=None):

        # Replace trigraph sequences
        t = ply.cpp.trigraph(input)
        lines = self.group_lines(t)

        if not source:
            source = ""
            
        self.define("__FILE__ \"%s\"" % source)

        self.source = source
        chunk = []
        enable = True
        iftrigger = False
        ifstack = []

        for x in lines:
            for i,tok in enumerate(x):
                if tok.type not in self.t_WS: break
            if tok.value == '#':
                # Preprocessor directive

                for tok in x:
                    if tok in self.t_WS and '\n' in tok.value:
                        chunk.append(tok)
                
                dirtokens = self.tokenstrip(x[i+1:])
                if dirtokens:
                    name = dirtokens[0].value
                    args = self.tokenstrip(dirtokens[1:])
                else:
                    name = ""
                    args = []
                
                if name == 'define':
                    if enable:
                        for tok in self.expand_macros(chunk):
                            yield tok
                        chunk = []
                        self.define(args)
                    chunk.append(x[-1])
                elif name == 'include':
                    if enable:
                        for tok in self.expand_macros(chunk):
                            yield tok
                        chunk = []
                        oldfile = self.macros['__FILE__']
                        for tok in self.include(args):
                            yield tok
                        self.macros['__FILE__'] = oldfile
                        self.source = source
                    chunk.append(x[-1])
                elif name == 'undef':
                    if enable:
                        for tok in self.expand_macros(chunk):
                            yield tok
                        chunk = []
                        self.undef(args)
                    chunk.append(x[-1])
                elif name == 'ifdef':
                    ifstack.append((enable,iftrigger))
                    if enable:
                        if not args[0].value in self.macros:
                            enable = False
                            iftrigger = False
                        else:
                            iftrigger = True
                    chunk.append(x[-1])
                elif name == 'ifndef':
                    ifstack.append((enable,iftrigger))
                    if enable:
                        if args[0].value in self.macros:
                            enable = False
                            iftrigger = False
                        else:
                            iftrigger = True
                    chunk.append(x[-1])
                elif name == 'if':
                    ifstack.append((enable,iftrigger))
                    if enable:
                        result = self.evalexpr(args)
                        if not result:
                            enable = False
                            iftrigger = False
                        else:
                            iftrigger = True
                    chunk.append(x[-1])
                elif name == 'elif':
                    if ifstack:
                        if ifstack[-1][0]:     # We only pay attention if outer "if" allows this
                            if enable:         # If already true, we flip enable False
                                enable = False
                            elif not iftrigger:   # If False, but not triggered yet, we'll check expression
                                result = self.evalexpr(args)
                                if result:
                                    enable  = True
                                    iftrigger = True
                    else:
                        self.error(self.source,dirtokens[0].lineno,"Misplaced #elif")
                    chunk.append(x[-1])
                        
                elif name == 'else':
                    if ifstack:
                        if ifstack[-1][0]:
                            if enable:
                                enable = False
                            elif not iftrigger:
                                enable = True
                                iftrigger = True
                    else:
                        self.error(self.source,dirtokens[0].lineno,"Misplaced #else")
                    chunk.append(x[-1])

                elif name == 'endif':
                    if ifstack:
                        enable,iftrigger = ifstack.pop()
                    else:
                        self.error(self.source,dirtokens[0].lineno,"Misplaced #endif")
                    chunk.append(x[-1])
                elif name == 'pragma':
                    chunk.extend(x)
                else:
                    # Unknown preprocessor directive
                    pass

            else:
                # Normal text
                if enable:
                    chunk.extend(x)

        for tok in self.expand_macros(chunk):
            yield tok
        chunk = []

class PreprocessorTokenGenerator(object):
    def __init__(self, f, source=None):
        self.pp = CustomizedPreprocessor(lexer=ply.lex.lex(ply.cpp))
        self.pp.parse(f.read(), source or hasattr(f, 'name') and f.name or None)
        self.lineno = 1
        self.lexpos = 0

    @property
    def source(self):
        return self.pp.source

    def next(self):
        t = self.pp.token()
        if t is None:
            raise StopIteration
        self.lineno = t.lineno
        self.lexpos = t.lexpos
        return t

    def __iter__(self):
        return self

def new_token(type, value, lineno, lexpos):
    retval = ply.lex.LexToken()
    retval.type = type
    retval.value = value
    retval.lineno = lineno
    retval.lexpos = lexpos
    return retval

def insert_line_directive(token_generator):
    need_insertion = True
    for t in token_generator:
        if t.type == 'CPP_COMMENT':
            if t.value.count('\n') > 1:
                need_insertion = True
            else:
                yield new_token('CPP_WS', "\n",
                                token_generator.lineno, token_generator.lexpos)
            continue
        if need_insertion:
            yield new_token('CPP_POUND', '#',
                            token_generator.lineno, token_generator.lexpos)
            yield new_token('CPP_WS', ' ',
                            token_generator.lineno, token_generator.lexpos)
            yield new_token('CPP_INTEGER', str(token_generator.lineno),
                            token_generator.lineno, token_generator.lexpos)
            yield new_token('CPP_WS', ' ',
                            token_generator.lineno, token_generator.lexpos)
            yield new_token('CPP_STRING', '"%s"' % litescape(token_generator.source),
                            token_generator.lineno, token_generator.lexpos)
            yield new_token('CPP_WS', "\n",
                            token_generator.lineno, token_generator.lexpos)
            need_insertion = False
        yield t

def preprocess(f, source=None):
    return ''.join(t.value for t in insert_line_directive(PreprocessorTokenGenerator(f, source)))

