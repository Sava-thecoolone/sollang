import sys
import random
from Nodes import *
from Parser import Parser
import importlib
import time

def printarr(scope, arr):
    a = arr.eval(scope).value
    if isinstance(a, Array):
        a = a.eval(scope).value
    print("[", end="")
    for e in range(len(a)):
        if isinstance(a[e].value, Array):
            printarr(scope, a[e].value)
        else:
            print(str(a[e].value), end="")
        if e < len(arr.eval(scope).value)-1:
            print(", ", end="")
    print("]")

def unpoint(val):
    if not isinstance(val, Point): return val
    if isinstance(val.value, list):
        return [unpoint(v) for v in val.value]
    if isinstance(val.value, dict):
        return {k: unpoint(v) for k, v in val.value.items()}
    return val.value

def metadecl(scope, args):
    scope[str(args[0].eval(scope).value)] = args[1].eval(scope)

def arrtodict(arr):
    dict = {}
    for i in arr:
        dict[i[0]] = i[1]
    return dict

def catch(scope, line, node):
    try:
        return node.eval(scope)
    except ASTException as e:
        return Point(Error(str(e)))
    except Exception as e:
        return Point(Error("line "+str(line)+" - "+str(e)))

def tryeval(scope, line, node):
    if not isinstance(node, ASTNode):
        raise ASTException("line "+str(line)+" - attempt to eval "+str(nametype(node)))
    else:
        return node.eval(scope)

def raiseerr(line, err):
    raise ASTException("line "+str(line)+" - "+err)

def evalgetbody(scope, node):
    node.eval(scope)
    return node

def nodeassert(scope, line, pval1, val2):
    val1 = unpoint(pval1)
    if val1 != val2:
        raise ASTException("line "+str(line)+" - "+str(nametype(val1))+" "+str(val1)+" doesn't equal "+str(nametype(val2))+" "+str(val2))
    return pval1

def readfile(name):
    with open(name, "r") as f:
        return f.read()

def writefile(name, val):
    with open(name, "w") as f:
        return f.write(val)

def loadfile(name):
    with open(name, "r") as f:
        parser = Parser()
        val = parser.parseStr(defaultscope, f.read())
        return val

def popandret(dict, val):
    newdict = dict.copy()
    newdict.pop(val, None)
    return newdict

def copyany(val):
    if not hasattr(val, "copy"):
        return val
    return val.copy()

def haskey(obj, val):
    return Point(val in obj)

def getkey(line, obj, val):
    if not val in obj:
        raise ASTException("line "+str(line)+" - invalid key \'"+str(val)+"\'")
    return obj[val]

def loadmodule(line, module):
    if isinstance(module, list):
        return Point([loadmodule(line, v) for v in module])
    if isinstance(module, dict):
        return Point({k: loadmodule(line, v) for k, v in module.items()})
    if callable(module):
        return Point(RawFunction(line, lambda scope, args: Point(module(*map(lambda x: x.eval(scope).value, args)))))
    return Point(module)

def importffi(line, name):
    return loadmodule(line, vars(importlib.import_module(name)))

defaultnopoint = {
    "copy": RawFunction(None, lambda scope, args: Point(copyany(args[0].eval(scope).value))),
    "print": RawFunction(None, lambda scope, args: print(*list(map(lambda x: str(unpoint(x.eval(scope))), args)))),
    "printraw": RawFunction(None, lambda scope, args: print(*args)),
    "printnoeval": RawFunction(None, lambda scope, args: print(*list(map(lambda x: str(unpoint(x.eval(scope, raw=True))), args)))),
    "printarr": RawFunction(None, lambda scope, args: printarr(scope, args[0])),
    "autoeval": RawFunction(None, lambda scope, args: Point(AutoExec(args[0].eval(scope).value))),
    "uneval": RawFunction(None, lambda scope, args: Point(Any(args[0].line, args[0].eval(scope).value))),
    "eval": RawFunction(None, lambda scope, args: tryeval(scope, args[0].line, args[0].eval(scope).value)),
    "evalwith": RawFunction(None, lambda scope, args: tryeval(scope|arrtodict(args[1].eval(scope).value), args[0].line, args[0].eval(scope).value)),
    "type": RawFunction(None, lambda scope, args: Point(nametype(args[0].eval(scope).value))),
    "typeraw": RawFunction(None, lambda scope, args: Point(nametype(args[0].eval(scope, raw=True).value))),
    "len": RawFunction(None, lambda scope, args: Point(len(args[0].eval(scope).value))),
    "abs": RawFunction(None, lambda scope, args: Point(abs(args[0].eval(scope).value))),
    "tostr": RawFunction(None, lambda scope, args: Point(str(args[0].eval(scope).value))),
    "haskey": RawFunction(None, lambda scope, args: haskey(args[0].eval(scope).value, str(args[1].eval(scope).value))),
    "getkey": RawFunction(None, lambda scope, args: getkey(args[0].line, args[0].eval(scope).value, str(args[1].eval(scope).value))),
    "MAX_FLOAT": sys.float_info.max,
    "MAX_INT": sys.maxsize,
    "MIN_INT": -sys.maxsize,
    "INF": float("inf"),
    "NaN": float("NaN"),
    "_": None,
    "random": RawFunction(None, lambda scope, args: Point(random.random())),
    "shuffle": RawFunction(None, lambda scope, args: Point(random.shuffle(args[0].eval(scope).value))),
    "metadeclare": RawFunction(None, lambda scope, args: metadecl(scope, args)),
    "append": RawFunction(None, lambda scope, args: args[0].eval(scope).value.append(args[1].eval(scope))),
    "try": RawFunction(None, lambda scope, args: catch(scope, args[0].line, args[0])),
    "assert": RawFunction(None, lambda scope, args: nodeassert(scope, args[0].line, args[0].eval(scope), unpoint(args[1].eval(scope)))),
    "throw": RawFunction(None, lambda scope, args: raiseerr(args[0].line, args[0].eval(scope).value)),
    "geterrmsg": RawFunction(None, lambda scope, args: Point(args[0].eval(scope).value.message)),
    "exit": RawFunction(None, lambda scope, args: exit(0)),
    "readfile": RawFunction(None, lambda scope, args: Point(readfile(args[0].eval(scope).value))),
    "writefile": RawFunction(None, lambda scope, args: Point(writefile(args[0].eval(scope).value))),
    "loadfile": RawFunction(None, lambda scope, args: Point(loadfile(args[0].eval(scope).value))),
    "run": RawFunction(None, lambda scope, args: loadfile(args[0].eval(scope).value).value.eval(scope)),
    "importffi": RawFunction(None, lambda scope, args: importffi(args[0], args[0].eval(scope).value)),
    "time": RawFunction(None, lambda scope, args: Point(time.time())),
    ":exit": AutoExec(Call(-1, Point(RawFunction(None, lambda scope, args: exit(0))), {})),
    ":help": """:builtins - print all functions in the default scope
:scope - print the current scope (inline for compile-time scope)
:help - print this message
:exit - exit the REPL
""",
    ":builtins": AutoExec(Call(-1, Point(RawFunction(None, lambda scope, args: Point(list(map(Point, list(defaultnopoint.keys())))))), {})),
    ":scope": AutoExec(Call(-1, Point(RawFunction(None, lambda scope, args: Point(popandret(scope, ":scope")))), {}))
}

defaultscope = {}
for k, v in defaultnopoint.items():
    defaultscope[k]=Point(v)

if __name__ == '__main__':
    print("\\\\b"+"|".join(defaultnopoint.keys())+"\\\\b")