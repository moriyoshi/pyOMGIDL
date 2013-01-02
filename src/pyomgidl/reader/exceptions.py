class IDLSyntaxError(Exception):
    @property
    def lineno(self):
        return len(self.args) >= 2 and self.args[1] or None

    @property
    def message(self):
        return self.args[0]

    def __str__(self):
        lineno = self.lineno
        if lineno:
            return '%s at line %d' % (self.message, lineno)
        else:
            return self.message

    def __init__(self, message, lineno=None):
        super(IDLSyntaxError, self).__init__(message, lineno)
