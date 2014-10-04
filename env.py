import sys
from llvm.core import Type

class Environ(object):
    def __init__(self, toplevel, types, names, module):
        self.toplevel = toplevel
        self.module = module
        self.types = types
        self.names = names
        self.module = module
        self.constants = {}

    def read_type(self, expr):
        if expr.issym:
            name = expr.assym.rstrip("*")
            if name in self.types:
                tp = self.types[name]
            for i in range(len(name), len(expr.assym)):
                tp = Type.pointer(tp)
            return tp
        sys.stderr.write("type missing: {}".format(expr))        
        sys.exit(1)

    def read_functype(self, expr):
        if expr.islist:
            ts = [self.read_type(a) for a in expr]
            return Type.function(ts.pop(0), ts)
        return self.read_type(expr)

    def constant(self, value):
        if value in self.constants:
            return self.constants[value]
        var = self.module.add_global_variable(value.type, "g{}".format(len(self.constants)))
        var.initializer = value
        var.global_constant = True
        self.constants[value] = var
        return var
