from Parser import Parser
from default_lib import defaultscope, unpoint
from Nodes import ASTException, Function
from pygments.styles import get_style_by_name
from prompt_toolkit import ANSI
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from Syntax import SyntaxLexer, SyntaxCompleter
import sys

style = style_from_pygments_cls(get_style_by_name("github-dark"))
session = PromptSession()
kb = KeyBindings()

def getindent(string):
    for i in range(len(string)):
        if string[i] != " ":
            return i
    return len(string)

if __name__ == '__main__':
    compscope = defaultscope.copy()
    evalscope = defaultscope.copy()
    parser = Parser()
    lexer = SyntaxLexer(compscope, evalscope)
    completer = SyntaxCompleter(compscope, evalscope)

    if len(sys.argv) > 1:
        flags = []
        while len(sys.argv) > 1 and sys.argv[1][0] == "-":
            flags.append(sys.argv[1])
            sys.argv.pop(1)
        inp = ""
        with open(sys.argv[1], "r") as f:
            inp = f.read()
        expr = parser.parseStr(compscope, inp)
        if "-ast" in flags:
            print(str(expr))
        else:
            val = unpoint(expr.value.eval(evalscope))
            if val is not None:
                print(str(val))
    else:
        @kb.add("enter")
        def _(event):
            buff = event.app.current_buffer
            level = parser.unexpectedEOF(compscope, buff.text)
            if level is not None:
                buff.insert_text("\n"+"    "*level)
            else:
                buff.history.append_string(buff.text)
                event.app.exit(result=buff.text)
        @kb.add("tab")
        def _(event):
            buff = event.app.current_buffer
            if buff.complete_state:
                index = buff.complete_state.complete_index
                if index == None:
                    index = 0
                elif buff.complete_state.complete_index == len(buff.complete_state.completions)-1:
                    index = None
                if index is not None and buff.complete_state.completions[index].text == "end":
                    buff.delete_before_cursor(4+(buff.cursor_position-buff.complete_state.completions[index].start_position))
                    buff.insert_text("end")
                else:
                    buff.complete_next()
            else:
                buff.start_completion(select_first=False)
        
        print("Welcome to SOL v1.0 - SecondOrderLanguage REPL\ntype :help for help\n")
        while True:
            inp = session.prompt(ANSI("\033[36m>>> \033[0m"), lexer=lexer, style=style, include_default_pygments_style=False, key_bindings=kb, completer=completer)
            try:
                expr = parser.parseStr(compscope, inp)
                val = unpoint(expr.value.eval(evalscope))
                if val is not None:
                    print(str(val)[:300]+("..." if len(str(val)) > 300 else ""))
            except ASTException as e:
                print("\033[31m"+str(e)+"\033[0m")