import regex
from collections.abc import Callable
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text.base import StyleAndTextTuples
from prompt_toolkit.completion import Completer, Completion
from default_lib import unpoint
from Nodes import Point

tokens = [
    ("class:pygments.literal.string", r'"(?(?=\\)..|.)*?"'),
    ("class:pygments.literal.string", r'r"(?(?=\\)..|.)*?"'),
    ("class:pygments.literal.number", r"\d*\.\d+"),
    ("class:pygments.literal.number", r"\d+"),
    ("class:pygments.literal.number", r"true|false"),
    ("class:pygments.operator", r"\+\+|--"),
    ("class:pygments.operator", r"\+=|-=|\*=|/="),
    ("class:pygments.punctuation", r"<:"),
    ("class:pygments.punctuation", r":>"),
    ("class:pygments.operator", r"<=|\?\?|>=|==|!=|//|\.\.|[+\-*\/%<>!|&\^]"),
    ("class:pygments.punctuation", r","),
    ("class:pygments.punctuation", r"\."),
    ("class:pygments.operator", r"="),
    ("class:pygments.punctuation", r"\("),
    ("class:pygments.punctuation", r"\)"),
    ("class:pygments.punctuation", r"\{"),
    ("class:pygments.punctuation", r"\}"),
    ("class:pygments.punctuation", r"\["),
    ("class:pygments.punctuation", r"\]"),
    ("class:pygments.keyword", r"declare"),
    ("class:pygments.keyword", r"end"),
    ("class:pygments.keyword", r"if"),
    ("class:pygments.keyword", r"else"),
    ("class:pygments.keyword", r"while"),
    ("class:pygments.keyword", r"foreach"),
    ("class:pygments.keyword", r"for"),
    ("class:pygments.keyword", r"function"),
    ("class:pygments.keyword", r"inline"),
    ("class:pygments.keyword", r"return"),
    ("class:pygments.keyword", r"break"),
    ("class:pygments.keyword", r"continue"),
    ("class:pygments.name.variable", r"[a-zA-Z0-9_:]+")
]

keywords = [
    "declare", "end", "if", "for", "foreach", "while", "function", "inline", "return", "break", "continue"
]

def nametype(val):
    return "<"+type(val).__name__+">"

class SyntaxLexer(Lexer):
    def __init__(self, compscope, evalscope):
        self.compscope = compscope
        self.evalscope = evalscope
        self.extend = []
        super().__init__()
    
    def nexttoken(self, string):
        for token, rule in tokens:
            if regex.match(r"\s*#", string):
                comm = regex.match(r"\s*.*?$", string, flags=regex.MULTILINE)
                return ("class:pygments.comment", comm)
            match = regex.match(r"\s*("+rule+")", string)
            if match:
                return (token, match)
        return None

    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        lines = document.lines
        def getline(line):
            out = []
            input = lines[line]
            pos = 0
            while pos < len(input):
                token = self.nexttoken(input[pos:])
                if token == None:
                    out.append(("class:pygments.punctuation", input[pos:]))
                    break
                else:
                    out.append((token[0], token[1].group()))
                pos += token[1].end()
            return out
        return getline

class SyntaxCompleter(Completer):
    def __init__(self, compscope, evalscope):
        self.compscope = compscope
        self.evalscope = evalscope
        super().__init__()

    def get_completions(self, document, complete_event):
        start = regex.search(r"[a-zA-Z0-9_:.]*$", document.text[:document.cursor_position]).start()
        end = regex.search(r"^[a-zA-Z0-9_:.]*", document.text[document.cursor_position:]).end()
        tokenSeq = document.text[start:end+document.cursor_position].split(".")
        curscope = unpoint(Point(self.compscope.copy())) if document.get_word_before_cursor() == "inline" else unpoint(Point(self.evalscope.copy()))
        for tokenIdx in range(len(tokenSeq)):
            curToken = tokenSeq[tokenIdx]
            if len(curToken) != 0:
                for i in keywords:
                    if str(i)[:len(curToken)] == curToken:
                        yield Completion(i, start_position=-len(curToken))
            if len(curToken) != 0 or len(tokenSeq) > 1:
                for i in curscope:
                    if str(i)[:len(curToken)] == curToken:
                        if tokenIdx == len(tokenSeq)-1:
                            yield Completion(i, start_position=-len(curToken))
                        else:
                            try:
                                curscope = curscope[curToken]
                                if not isinstance(curscope, dict):
                                    return
                            except:
                                return