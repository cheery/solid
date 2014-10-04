import sys
from llvm.core import Constant, Type

class Context(object):
    def __init__(self, prog, bb, env, locl):
        self.prog = prog
        self.bb = bb
        self.env = env
        self.locl = locl
        self.closed = False

    def expr(self, expr):
        if expr.islist and len(expr) > 0:
            unit = self.expr(expr[0])
            if not unit.noret:
                return unit.call(self, expr)
        return self.atom(expr)

    def stmt(self, expr):
        if expr.islist and len(expr) > 0:
            unit = self.expr(expr[0])
            return unit(self, expr)
        sys.stderr.write("not an stmt: {}\n".format(expr))
        sys.exit(1)

    def atom(self, expr):
        if expr.assym in self.locl:
            return self.locl[expr.assym]
        if expr.assym in self.env.names:
            return self.env.names[expr.assym]
        if expr.isnum:
            return Constant.int(Type.int(), expr.value)
        if expr.isstring:
            s = Constant.stringz(expr.value.encode('utf-8'))
            mem = self.env.constant(s)
            return self.bb.gep(mem, [Constant.int(Type.int(), 0)]*2)
        sys.stderr.write("atom undefined {}\n".format(expr))
        sys.exit(1)
