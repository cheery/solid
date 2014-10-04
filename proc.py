import sys
from llvm.core import Builder, FunctionType
from context import Context

def macro(env, stmt, defer):
    if len(stmt) < 4:
        malformed(stmt)
    head, name, spec, args = stmt[:4]
    body = stmt[4:]
    if not name.issym:
        malformed(stmt)
    if not args.islist:
        malformed(stmt)
    spec = env.read_functype(spec)

    argl = []
    for a in args:
        if not a.issym:
            sys.stderr.write("invalid argument name: {}\n".format(a))
            sys.exit(1)
        argl.append(a.assym)

    if not isinstance(spec, FunctionType):
        sys.stderr.write("invalid function signature: {}\n".format(spec))
        sys.exit(1)

    proc = env.module.add_function(spec, name.assym)
    env.names[name.assym] = prog = Procedure(proc, spec)

    bb = Builder.new(proc.append_basic_block('entry'))
    context = Context(proc, bb, env, locl=dict(zip(argl, proc.args)))

    noret = env.types['void'] == spec.return_type

    @defer.append
    def build():
        for stmt in body:
            context.stmt(stmt)

        if not context.closed:
            if noret:
                context.bb.ret_void()
                context.closed = True
            else:
                sys.stderr.write("missing return {}\n".format(stmt))

def malformed(stmt):
    sys.stderr.write("malformed proc: {}\n".format(stmt))
    sys.exit(1)

class Procedure(object):
    def __init__(self, proc, type):
        self.proc = proc
        self.type = type

    def __call__(self, context, expr):
        args = [context.expr(a) for a in expr[1:]]
        return context.bb.call(self.proc, args)
