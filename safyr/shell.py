from lexer import Lexer
from parser import Parser
from interpreter import *
from sys import exit


def help():
    print("Command          Effect")
    print("________________________________________________________________________________")
    print("help             Print this message")
    print("q                Exit the shell")
    print("run <filename>   Execute the code contained in filename.sfr (exclude the '.sfr')")
    print("<expression>     Evaluate the SAFyR expression entered")


class Shell:

    def __init__(self):
        print('Initializing Safyr Shell Environment')
        print('Type help for some example commands.')
        self.run()

    def run(self):
        global_symbol_table = SymbolTable()
        global_symbol_table.set("null", Number(0))
        global_symbol_table.set("T", Number(1))
        global_symbol_table.set("F", Number(0))
        global_symbol_table.set('static-typing', Number(0))
        global_symbol_table.set("print", BuiltInFunction.print)
        global_symbol_table.set("rprint", BuiltInFunction.rprint)
        global_symbol_table.set("INPUT", BuiltInFunction.input)
        global_symbol_table.set("INPUT_INT", BuiltInFunction.input_int)
        global_symbol_table.set("CLEAR", BuiltInFunction.clear)
        global_symbol_table.set("CLS", BuiltInFunction.clear)
        global_symbol_table.set("isnum", BuiltInFunction.is_number)
        global_symbol_table.set("isstr", BuiltInFunction.is_string)
        global_symbol_table.set("islst", BuiltInFunction.is_list)
        global_symbol_table.set("isfun", BuiltInFunction.is_function)
        global_symbol_table.set("pop", BuiltInFunction.pop)
        global_symbol_table.set("append", BuiltInFunction.append)
        global_symbol_table.set("extend", BuiltInFunction.extend)
        global_symbol_table.set("keys", BuiltInFunction.keys)
        global_symbol_table.set("values", BuiltInFunction.values)
        global_symbol_table.set("open", BuiltInFunction.open)
        global_symbol_table.set("read", BuiltInFunction.read)
        global_symbol_table.set("write", BuiltInFunction.write)
        global_symbol_table.set("close", BuiltInFunction.close)
        global_symbol_table.set("range", BuiltInFunction.range)
        global_symbol_table.set("rand", BuiltInFunction.rand)
        global_symbol_table.set("len", BuiltInFunction.len)
        global_symbol_table.set("type", BuiltInFunction.type)

        context = Context('<program>')
        context.symbol_table = global_symbol_table
        context.symbol_table.globals = list(global_symbol_table.symbols.keys())

        while True:

            cmd = input('>> ')
            if cmd == 'q': break
            if cmd == 'help':
                help()
                continue

            needsrun = False
            data = ''
            fromfile = False
            if cmd.startswith('run '):
                cmd = cmd[4:]
                if os.path.exists(cmd + '.sfr'):
                    with open(cmd + '.sfr', 'r') as f:
                        data = f.read()
                        needsrun = True
                        fromfile = True
                else: print(f'File not found: {cmd}')
            else:
                data = cmd
                needsrun = True

            if needsrun:
                lex = Lexer()
                toks = lex.tokenize(data)
                if toks.error:
                    print(toks.error)
                    continue

                par = Parser(toks.value, global_symbol_table)
                ast = par.parse()
                if ast.error:
                    print(f'Exception encountered in parser:\n\t{ast.error}')
                    continue

                context = Context('<program>')
                context.symbol_table = global_symbol_table
                result = Interpreter().visit(ast.node, context)
                if result.error:
                    print(result.error)
                    continue

                # this helps the test suite see the answer, but is otherwise useless
                result.value
                if not fromfile:
                    print(result.value)


if __name__ == '__main__':
    Shell().run()
