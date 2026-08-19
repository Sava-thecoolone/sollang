import regex

tokens = [
    ("STR", r'"(?(?=\\)(.).|.)*?"'),
    ("RSTR", r'r"(?(?=\\)(.).|.)*?"'),
    ("FLOAT", r"\d*\.\d+"),
    ("INT", r"\d+"),
    ("BOOL", r"true|false"),
    ("SPUNOP", r"\+\+|--"),
    ("SPBINOP", r"\+=|-=|\*=|/="),
    ("LOBJ", r"<:"),
    ("ROBJ", r":>"),
    ("OP", r"<=|\?\?|>=|==|!=|//|\.\.|[+\-*\/%<>!|&\^]"),
    ("COM", r","),
    ("PERIOD", r"\."),
    ("EQ", r"="),
    ("LPAR", r"\("),
    ("RPAR", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("LSQR", r"\["),
    ("RSQR", r"\]"),
    ("DECL", r"declare"),
    ("END", r"end"),
    ("IF", r"if"),
    ("ELSE", r"else"),
    ("WHILE", r"while"),
    ("FOREACH", r"foreach"),
    ("FOR", r"for"),
    ("FUNC", r"function"),
    ("INLN", r"inline"),
    ("RET", r"return"),
    ("BREAK", r"break"),
    ("CONT", r"continue"),
    ("VAR", r"[a-zA-Z0-9_:]+")
]

def nametype(val):
    return "<"+type(val).__name__+">"

class Lexer:
    def gettokens(self, input) -> list:
        out = []
        pos = 0
        line = 1
        while pos < len(input):
            foundMatch = False
            for token, rule in tokens:
                if regex.match(r"^\s*#", input[pos:]):
                    comm = regex.match(r"\A\s*.*?$", input[pos:], flags=regex.MULTILINE)
                    line += comm.group().count("\n")
                    pos += comm.end()
                    foundMatch = True
                    break
                match = regex.search(r"^\s*("+rule+")", input[pos:])
                if match:
                    out.append((token, match.captures(0)[0].strip(), line))
                    line += match.group().count("\n")
                    pos += match.end()
                    foundMatch = True
                    break
            if len(input[pos:].strip()) == 0:
                break
            if not foundMatch:
                raise SyntaxError("line "+str(line)+" - invalid token \'"+regex.match(r"^\s*\w*", input[pos:]).group().strip()+"\' at position "+str(pos))

        out.append(("EOF", "", line))
        return out