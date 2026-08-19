import codecs
from Lexer import Lexer
from Nodes import *

def nametype(val):
    return "<"+type(val).__name__+">"

exprStarts = ("LPAR", "LBRACE", "LOBJ", "LSQR", "INT", "FLOAT", "STR", "VAR", "OP", "IF", "WHILE", "DECL", "FOR", "FOREACH", "FUNC", "INLN")
exprEnds =   ("INT", "FLOAT", "STR", "VAR", "RPAR", "RBRACE", "ROBJ", "END")

precedence = [
    ("??"),
    ("|", "&"),
    ("==", "!=", ">", "<", "<=", ">="),
    (".."),
    ("++", "--", "+", "-"),
    ("*", "/", "//", "%"),
    ("^")
]

class Parser:
    def __init__(self):
        self.lexer = Lexer()

    def peek(self):
        return self.tokens[self.curToken]

    def multipeek(self, no):
        return self.tokens[self.curToken+no]
    
    def eat(self, token):
        gotToken = self.peek()
        if gotToken[0] != token:
            raise ASTException("line "+str(self.line)+" - unexpected token "+gotToken[0]+" - expected "+token)
        self.curToken += 1
        self.line = self.peek()[2]
        return gotToken
    
    def parseExpr(self, scope):
        return self.parsePrec(scope, 0)

    def parsePrec(self, scope, prec):
        if len(precedence) <= prec:
            expr = self.parseHighest(scope)
            while self.peek()[0] in ("PERIOD", "LPAR", "LSQR", "EQ"):
                if self.peek()[0] == "PERIOD":
                    self.eat("PERIOD")
                    expr = Point(GetKey(self.line, expr, self.eat("VAR")[1]))
                if self.peek()[0] == "LPAR":
                    self.eat("LPAR")
                    args = []
                    while self.peek()[0] != "RPAR":
                        args.append(self.parseExpr(scope))
                        if self.peek()[0] == "COM": self.eat("COM")
                    self.eat("RPAR")
                    expr = Point(Call(self.line, expr, args))
                if self.peek()[0] == "LSQR":
                    self.eat("LSQR")
                    idx = self.parseExpr(scope)
                    self.eat("RSQR")
                    expr = Point(ArrRead(self.line, expr, idx))
                if self.peek()[0] == "EQ":
                    self.eat("EQ")
                    expr = Point(Assign(self.line, expr, self.parseExpr(scope)))
            if self.peek()[0] == "SPUNOP":
                op = self.eat("SPUNOP")
                expr = Point(SpecOper(self.line, expr, op[1], None))
            elif self.peek()[0] == "SPBINOP":
                op = self.eat("SPBINOP")
                right = self.parseExpr(scope)
                expr = Point(SpecOper(self.line, expr, op[1], right))
            return expr
        else:
            left = self.parsePrec(scope, prec+1)
            while self.peek()[0] != "EOF" and self.peek()[1] in precedence[prec]:
                op = self.eat("OP")
                if op[1] == "^":
                    right = self.parsePrec(scope, prec)
                else:
                    right = self.parsePrec(scope, prec+1)
                left = Point(BinOper(op[2], left, op[1], right))
            return left
    
    def parseHighest(self, scope):
        token = self.peek()
        if token[0] == "INT":
            self.eat("INT")
            return Point(Integer(token[2], token[1]))
        elif token[0] == "FLOAT":
            self.eat("FLOAT")
            return Point(Float(token[2], token[1]))
        elif token[0] == "BOOL":
            self.eat("BOOL")
            return Point(Boolean(token[2], token[1]))
        elif token[0] == "STR":
            self.eat("STR")
            return Point(String(token[2], codecs.decode(token[1][1:-1], "unicode_escape")))
        elif token[0] == "RSTR":
            self.eat("RSTR")
            return Point(String(token[2], token[1][2:-1]))
        elif token[0] == "VAR":
            self.eat("VAR")
            return Point(Variable(token[2], token[1]))
        elif token[0] == "LPAR":
            self.eat("LPAR")
            expr = self.parseExpr(scope)
            self.eat("RPAR")
            return expr
        elif token[0] == "OP":
            return Point(UnOper(token[2], self.eat("OP")[1], self.parseHighest(scope)))
        elif token[0] == "FUNC":
            self.eat("FUNC")
            self.eat("LPAR")
            args = []
            while self.peek()[0] != "RPAR":
                args.append(self.eat("VAR")[1])
                if self.peek()[0] == "COM": self.eat("COM")
            self.eat("RPAR")
            return self.parseFunc(scope, args)
        elif token[0] == "IF":
            self.eat("IF")
            expr = self.parseExpr(scope)
            return self.parseIf(scope, expr)
        elif token[0] == "WHILE":
            self.eat("WHILE")
            expr = self.parseExpr(scope)
            return self.parseWhile(scope, expr)
        elif token[0] == "FOR":
            self.eat("FOR")
            return self.parseFor(scope)
        elif token[0] == "FOREACH":
            self.eat("FOREACH")
            return self.parseForeach(scope)
        elif token[0] == "LBRACE":
            self.eat("LBRACE")
            expr = Point(Unexecuted(ReturnBody(self.parse(scope.copy(), "RBRACE"))))
            self.eat("RBRACE")
            return expr
        elif token[0] == "LOBJ":
            self.eat("LOBJ")
            items = {}
            while self.peek()[0] != "ROBJ":
                key = self.eat("VAR")[1]
                self.eat("EQ")
                items[key] = self.parseExpr(scope)
                if self.peek()[0] == "COM": self.eat("COM")
            self.eat("ROBJ")
            return Point(Object(token[2], items))
        elif token[0] == "LSQR":
            self.eat("LSQR")
            items = []
            while self.peek()[0] != "RSQR":
                expr = self.parseExpr(scope)
                items.append(expr)
                if self.peek()[0] == "COM": self.eat("COM")
            self.eat("RSQR")
            return Point(Array(token[2], items))
        elif token[0] == "INLN":
            self.eat("INLN")
            return Point(Any(token[2], self.parseExpr(scope).value.eval(scope).value))
        elif token[0] == "DECL":
            self.eat("DECL")
            var = self.eat("VAR")
            self.eat("EQ")
            return Point(Declare(var[2], var[1], self.parseExpr(scope)))
        raise ASTException("line "+str(token[2])+" - unexpected token "+token[0]+" in expression")

    def parseFunc(self, scope, args):
        point = Point(None)
        point.value = Function(self.line, Point(ReturnBody(self.parse(scope.copy(), ("END")))), args, point)
        self.eat("END")
        return point
    
    def parseIf(self, scope, expr):
        statement = Point(If(self.line, self.parse(scope.copy(), ("ELSE", "END")), Point(Program(self.line, [])), expr))
        if self.peek()[0] == "ELSE":
            self.eat("ELSE")
            statement.value.progFalse = self.parse(scope.copy(), ("END"))
        self.eat("END")
        return statement
    
    def parseWhile(self, scope, expr):
        statement = Point(While(self.line, self.parse(scope.copy(), ("END")), expr))
        self.eat("END")
        return statement
    
    def parseFor(self, scope):
        var = self.eat("VAR")
        self.eat("EQ")
        statements = [Point(Declare(self.line, var[1], self.parseExpr(scope))), Point(NoneNode())]
        expr = self.parseExpr(scope)
        expr2 = self.parseExpr(scope)
        statements[1] = Point(While(self.line, self.parse(scope.copy(), ("END")), expr))
        statements[1].value.prog.value.nodes.append(expr2)
        self.eat("END")
        return Point(Program(self.line, statements))
    
    def parseForeach(self, scope):
        var1 = self.eat("VAR")
        var2 = self.eat("VAR")
        expr = self.parseExpr(scope)
        body = self.parse(scope.copy(), ("END"))
        self.eat("END")
        return Point(Foreach(self.line, body, var1[1], var2[1], expr))
    
    def parse(self, scope, until):
        prog = Program(self.line, [])
        self.curLevel += 1
        while not (self.peek()[0] in until):
            token = self.peek()
            if token[0] == "FUNC" and (self.multipeek(1)[0] == "VAR" or (self.multipeek(1)[0] == "INLN" and self.multipeek(2)[0] == "VAR")):
                self.eat("FUNC")
                if self.peek()[0] == "INLN":
                    self.eat("INLN")
                    var = self.eat("VAR")
                    self.eat("LPAR")
                    args = []
                    while self.peek()[0] != "RPAR":
                        args.append(self.eat("VAR")[1])
                        if self.peek()[0] == "COM": self.eat("COM")
                    self.eat("RPAR")
                    scope[var[1]] = self.parseFunc(scope, args)
                    continue
                var = self.eat("VAR")
                self.eat("LPAR")
                args = []
                while self.peek()[0] != "RPAR":
                    args.append(self.eat("VAR")[1])
                    if self.peek()[0] == "COM": self.eat("COM")
                self.eat("RPAR")
                prog.nodes.append(Point(Declare(var[2], var[1], self.parseFunc(scope, args))))
            elif token[0] in exprStarts:
                prog.nodes.append(self.parseExpr(scope))
            elif token[0] == "RET":
                self.eat("RET")
                if self.peek()[0] in ("END", "EOF", "RBRACE"):
                    prog.nodes.append(Point(Return(Point(NoneNode()))))
                else:
                    prog.nodes.append(Point(Return(self.parseExpr(scope))))
            elif token[0] == "BREAK":
                self.eat("BREAK")
                if self.peek()[0] in {"END", "EOF", "RBRACE"}:
                    prog.nodes.append(Point(Break(Point(NoneNode()))))
                else:
                    prog.nodes.append(Point(Break(self.parseExpr(scope))))
            elif token[0] == "CONT":
                self.eat("CONT")
                prog.nodes.append(Point(Continue()))
            elif token[0] == "LAST":
                self.eat("LAST")
                expr = Point(Unexecuted(ReturnBody(self.parse(scope.copy(), "RAST"))))
                self.eat("RAST")
                prog.nodes.append(expr)
                prog.nodes.append(self.parseExpr(scope))
            else:
                raise ASTException("line "+str(self.line)+" - unexpected token "+token[0])
        self.curLevel -= 1
        return Point(prog)
    
    def parseStr(self, scope, input):
        self.tokens = self.lexer.gettokens(input)
        self.curToken = 0
        self.curLevel = 0
        self.line = 1
        return Point(ReturnBody(self.parse(scope, ("EOF"))))
    
    def unexpectedEOF(self, scope, input):
        try:
            self.parseStr(scope, input)
            return None
        except ASTException:
            if self.curToken != len(self.tokens)-1: return None
            return self.curLevel