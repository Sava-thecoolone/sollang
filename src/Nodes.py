def nametype(val):
    return "<"+type(val).__name__+">"

class Point(object):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return "<"+str(self.value)+">"

class ASTNode(object):
    pass

class ASTException(BaseException):
    def __init__(self, message):
        super().__init__(message)

class Unexecuted(ASTNode):
    def __init__(self, expr):
        self.expr = expr
        self.line = expr.line
    
    def __str__(self):
        return "(Unexec "+str(self.expr)+")"
    
    def eval(self, scope):
        return Point(self.expr)

class AutoExec(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    
    def __str__(self):
        return "(AutoExec "+str(self.expr)+")"
    
    def eval(self, scope):
        return self.expr.eval(scope)

class NoneNode(ASTNode):
    def __str__(self):
        return "(None)"
    
    def eval(self, scope):
        return Point(None)

class Error(ASTNode):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return "(Error "+str(self.message)+")"
    
    def eval(self, scope):
        return Point(self)

class Return(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    
    def __str__(self):
        return "(Return "+str(self.expr)+")"
    
    def eval(self, scope):
        return self.expr.value.eval(scope)

class Break(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    
    def __str__(self):
        return "(Break "+str(self.expr)+")"
    
    def eval(self, scope):
        return self.expr.value.eval(scope)

class Continue(ASTNode):
    def __str__(self):
        return "(Continue)"
    
    def eval(self, scope):
        return Point(self)
    
class ReturnBody(ASTNode):
    def __init__(self, expr):
        self.expr = expr
        self.line = expr.value.line
    
    def __str__(self):
        return "(Body "+str(self.expr)+")"
    
    def eval(self, scope):
        ret = self.expr.value.eval(scope)
        while ret is not None and isinstance(ret.value, Return):
            ret.value = ret.value.expr.value
        return ret

class Program(ASTNode):
    def __init__(self, line, nodes):
        self.nodes = nodes
        self.line = line
    
    def __str__(self):
        return "(Prog "+str(", ".join(map(str, self.nodes)))+")"
    
    def eval(self, scope):
        for i in range(len(self.nodes)-1):
            node = self.nodes[i].value
            if isinstance(node, Return):
                return Point(Return(node.eval(scope)))
            elif isinstance(node, Break):
                return Point(Break(node.eval(scope)))
            elif isinstance(node, Continue):
                break
            else:
                ret = node.eval(scope)
                if ret is not None and isinstance(ret.value, (Return, Break)):
                    return ret
        if len(self.nodes) != 0:
            node = self.nodes[len(self.nodes)-1].value
            if isinstance(node, Return):
                return Point(Return(node.eval(scope)))
            if isinstance(node, Break):
                return Point(Break(node.eval(scope)))
            ret = node.eval(scope)
            return ret
        else:
            return Point(None)

class Integer(ASTNode):
    def __init__(self, line, token):
        self.val = int(token)
        self.line = line
    
    def __str__(self):
        return "(Int "+str(self.val)+")"
    
    def eval(self, scope):
        return Point(self.val)

class Float(ASTNode):
    def __init__(self, line, token):
        self.val = float(token)
        self.line = line
    
    def __str__(self):
        return "(Float "+str(self.val)+")"
    
    def eval(self, scope):
        return Point(self.val)

class Boolean(ASTNode):
    def __init__(self, line, token):
        self.val = token == "true"
        self.line = line
    
    def __str__(self):
        return "(Bool "+str(self.val)+")"
    
    def eval(self, scope):
        return Point(self.val)

class String(ASTNode):
    def __init__(self, line, token):
        self.val = str(token)
        self.line = line
    
    def __str__(self):
        return "(Str "+self.val+")"
    
    def eval(self, scope):
        return Point(self.val)

class Any(ASTNode):
    def __init__(self, line, value):
        self.value = value
        self.line = line
    
    def __str__(self):
        return "(Any "+str(self.value)+")"
    
    def eval(self, scope):
        return Point(self.value)
    
class Array(ASTNode):
    def __init__(self, line, items):
        self.items = items
        self.line = line
    
    def __str__(self):
        return "(Arr "+str(", ".join(map(str, self.items[:10])))+("..." if len(self.items) > 10 else "")+")"
    
    def eval(self, scope):
        return Point(list(map(lambda v: v.value.eval(scope), self.items)))

class ArrRead(ASTNode):
    def __init__(self, line, arr, idx):
        self.arr = arr
        self.idx = idx
        self.line = line
    
    def __str__(self):
        return "(ArrRead "+str(self.arr)+", "+str(self.idx)+")"
    
    def eval(self, scope):
        arr = self.arr.value.eval(scope).value
        if not hasattr(arr, "__getitem__"):
            raise ASTException("line "+str(self.line)+" - attempt to index "+str(nametype(arr)))
        idx = self.idx.value.eval(scope).value
        if len(arr) <= idx or idx < 0:
            raise ASTException("line "+str(self.line)+" - array index "+str(idx)+" out of range")
        return arr[idx] if isinstance(arr[idx], Point) else Point(arr[idx])

class Object(ASTNode):
    def __init__(self, line, dict):
        self.dict = dict
        self.line = line
    
    def __str__(self):
        return "(Obj "+", ".join(str(k)+"="+str(v) for k, v in self.dict.items()[:10])+("..." if len(self.dict.items()) > 10 else "")+")"
    
    def eval(self, scope):
        point = Point(None)
        point.value = {k: (v.value.eval(scope) if not isinstance(v.value, Function) else Point(ContextFunction(self.line, v.value.prog, v.value.args, point))) for k, v in self.dict.items()}
        return point

class GetKey(ASTNode):
    def __init__(self, line, var, key):
        self.var = var
        self.key = key
        self.line = line
    
    def __str__(self):
        return "(Get "+str(self.var)+", "+str(self.key)+")"
    
    def eval(self, scope):
        var = self.var.value.eval(scope).value
        if isinstance(var, Object):
            var = var.eval(scope).value
        if not isinstance(var, dict):
            raise ASTException("line "+str(self.line)+" - attempt to key "+str(nametype(var)))
        if not self.key in var:
            raise ASTException("line "+str(self.line)+" - object key \'"+str(self.key)+"\' doesn't exist")
        return var[self.key]

class Variable(ASTNode):
    def __init__(self, line, name):
        self.name = name
        self.line = line
    
    def __str__(self):
        return "(Var "+str(self.name)+")"
    
    def eval(self, scope, raw=False):
        if self.name in scope:
            val = scope[self.name]
            if not raw and isinstance(val.value, AutoExec):
                return val.value.eval(scope)
                return point
            else:
                return val
        else:
            raise ASTException("line "+str(self.line)+" - undeclared variable \'"+self.name+"\'")

class Declare(ASTNode):
    def __init__(self, line, name, val):
        self.val = val
        self.name = name
        self.line = line
    
    def __str__(self):
        return "(Declare "+str(self.name)+", "+str(self.val)+")"
    
    def eval(self, scope):
        scope[self.name] = self.val.value.eval(scope)
        return scope[self.name]

class Assign(ASTNode):
    def __init__(self, line, var, val):
        self.val = val
        self.var = var
        self.line = line
    
    def __str__(self):
        return "(Assign "+str(self.var)+", "+str(self.val)+")"
    
    def eval(self, scope):
        var = self.var.value.eval(scope)
        var.value = self.val.value.eval(scope).value
        return var

class Function(ASTNode):
    def __init__(self, line, prog, args, context):
        self.prog = prog
        self.args = args
        self.line = line
        self.context = context
    
    def __str__(self):
        return "(Func {"+str(", ".join(map(str, self.args)))+"})"
    
    def call(self, scope, argVals):
        res = []
        for i in argVals:
            res.append(i.value.eval(scope))
        return self.prog.value.eval(scope|{"thisfunc": self.context}|dict(zip(self.args, res)))
    
    def eval(self, scope):
        return Point(self)
    
class RawFunction(ASTNode):
    def __init__(self, line, code):
        self.code = code
        self.line = line
    
    def __str__(self):
        return "(RawFunc)"
    
    def call(self, scope, argVals):
        res = []
        for i in argVals:
            res.append(i.value)
        ret = self.code(scope, res)
        return ret if ret is not None else Point(None)
    
    def eval(self, scope):
        return Point(self)

class ContextFunction(ASTNode):
    def __init__(self, line, prog, args, context):
        self.prog = prog
        self.args = args
        self.context = context
        self.line = line
    
    def __str__(self):
        return "(ConFunc {"+str(", ".join(map(str, self.args)))+"} "+str(self.prog)+")"
    
    def call(self, scope, argVals):
        res = []
        for i in argVals:
            res.append(i.eval(scope))
        return self.prog.value.eval(scope|{"this": self.context}|dict(zip(self.args, res)))
    
    def eval(self, scope):
        return Point(self)
    
class Call(ASTNode):
    def __init__(self, line, func, args):
        self.func = func
        self.args = args
        self.line = line
    
    def __str__(self):
        return "(Call "+str(self.func)+" {"+str(", ".join(map(str, self.args)))+"})"
    
    def eval(self, scope):
        func = self.func.value.eval(scope).value
        if not isinstance(func, (Function, RawFunction, ContextFunction)):
            raise ASTException("line "+str(self.line)+" - attempt to call "+str(nametype(func)))
        return func.call(scope, self.args)

class If(ASTNode):
    def __init__(self, line, progTrue, progFalse, expr):
        self.progTrue = progTrue
        self.progFalse = progFalse
        self.expr = expr
        self.line = line
    
    def __str__(self):
        return "(If {"+str(self.expr)+"} "+str(self.progTrue)+" : "+str(self.progFalse)+")"
    
    def eval(self, scope):
        if self.expr.value.eval(scope).value:
            return self.progTrue.value.eval(scope)
        else:
            return self.progFalse.value.eval(scope)

class While(ASTNode):
    def __init__(self, line, prog, expr):
        self.prog = prog
        self.expr = expr
        self.line = line
    
    def __str__(self):
        return "(While {"+str(self.expr)+"} "+str(self.prog)+")"
    
    def eval(self, scope):
        last = None
        while self.expr.value.eval(scope).value:
            last = self.prog.value.eval(scope)
            if isinstance(last.value, Return):
                return last
            elif isinstance(last.value, Break):
                return Point(last.value.expr)

class Foreach(ASTNode):
    def __init__(self, line, prog, var1, var2, expr):
        self.prog = prog
        self.var1 = var1
        self.var2 = var2
        self.expr = expr
        self.line = line
    
    def __str__(self):
        return "(While {"+str(self.expr)+"} "+str(self.prog)+")"
    
    def eval(self, scope):
        last = None
        arr = self.expr.value.eval(scope).value
        if isinstance(arr, dict):
            for i, j in arr.items():
                scope[self.var1] = Point(i)
                scope[self.var2] = j
                last = self.prog.value.eval(scope)
                if isinstance(last.value, Return):
                    return last
                elif isinstance(last.value, Break):
                    return Point(last.value.expr)
        else:
            for i in arr:
                scope[self.var1] = i
                last = self.prog.value.eval(scope)
                if isinstance(last.value, Return):
                    return last
                elif isinstance(last.value, Break):
                    return Point(last.value.expr)
        return last

class BinOper(ASTNode):
    def __init__(self, line, left, op, right):
        self.op = op
        self.left = left
        self.right = right
        self.line = line
    
    def __str__(self):
        return "(BinOp "+str(self.left)+", "+str(self.op)+", "+str(self.right)+")"
    
    def eval(self, scope):
        lval = self.left.value.eval(scope).value
        rval = self.right.value.eval(scope).value
        match self.op:
            case "+":
                return Point(lval + rval)
            case "-":
                return Point(lval - rval)
            case "*":
                return Point(lval * rval)
            case "/":
                return Point(lval / rval)
            case "//":
                return Point(lval // rval)
            case "%":
                return Point(lval % rval)
            case "^":
                return Point(lval ** rval)
            case "<":
                return Point(lval < rval)
            case ">":
                return Point(lval > rval)
            case "==":
                return Point(lval == rval)
            case ">=":
                return Point(lval >= rval)
            case "<=":
                return Point(lval <= rval)
            case "!=":
                return Point(lval != rval)
            case "&":
                return Point(lval and rval)
            case "|":
                return Point(lval or rval)
            case "??":
                return Point(lval if lval is not None else rval)
            case "..":
                return Point(list(map(lambda v: Point(v), range(lval, rval))))
        raise ASTException("line "+str(self.line)+" - invalid operator "+self.op)

class UnOper(ASTNode):
    def __init__(self, line, op, node):
        self.op = op
        self.node = node
        self.line = line
    
    def __str__(self):
        return "(UnOp "+str(self.op)+", "+str(self.node)+")"
    
    def eval(self, scope):
        val = self.node.value.eval(scope).value
        match self.op:
            case "-":
                return Point(-val)
            case "!":
                return Point(not val)
        raise ASTException("line "+str(self.line)+" - invalid operator "+self.op)

class SpecOper(ASTNode):
    def __init__(self, line, var, op, val):
        self.op = op
        self.var = var
        self.value = val
        self.line = line
    
    def __str__(self):
        return "(SpOp "+str(self.var)+", "+str(self.op)+(", "+str(self.value) if self.value is not None else "")+")"
    
    def eval(self, scope):
        var = self.var.value.eval(scope)
        match self.op:
            case "++":
                var.value += 1
            case "--":
                var.value -= 1
            case "+=":
                var.value += self.value.value.eval(scope).value
            case "-=":
                var.value -= self.value.value.eval(scope).value
            case "*=":
                var.value *= self.value.value.eval(scope).value
            case "/=":
                var.value /= self.value.value.eval(scope).value
            case _:
                raise ASTException("line "+str(self.line)+" - invalid operator "+self.op)
        return var