import unittest

from safyr.interpreter import *
from safyr.lexer import *
from safyr.parser import *
from safyr.constants import *

BRK = Token('EOF', None)
POS = Position(0,0,0,0,0)

def get_sym_table():
    global_symbol_table = SymbolTable()
    global_symbol_table.set("null", Number(0))
    global_symbol_table.set("T", Number(1))
    global_symbol_table.set("F", Number(0))
    global_symbol_table.set("static-typing", Number(0))
    global_symbol_table.globals = list(global_symbol_table.symbols.keys())

    global_symbol_table.set("print", BuiltInFunction.print)
    global_symbol_table.set("rprint", BuiltInFunction.rprint)
    global_symbol_table.set("input", BuiltInFunction.input)
    global_symbol_table.set("inputint", BuiltInFunction.input_int)
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

    global_symbol_table.globals = list(global_symbol_table.symbols.keys())

    return global_symbol_table


RUN = Interpreter()
context = Context('<test>', root=os.path.join(os.getcwd(), 'test'))

# BEGIN PARSER SECTION #

class TestParserErrors(unittest.TestCase):

    def test_unclosed_multiline_if(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1{\n1').value).parse().error
            if e: raise e

    def test_invalid_expression(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('1 + +').value).parse().error
            if e: raise e

    def test_begin_with_keyword(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('end=5').value).parse().error
            if e: raise e

    def test_use_invalid_input(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('use 123').value).parse().error
            if e: raise e

    def test_del_invalid_input(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('del 123').value).parse().error
            if e: raise e

    def test_use_toomuch_input(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('use abc 123').value).parse().error
            if e: raise e

    def test_invalid_call(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('print(a + )').value).parse().error
            if e: raise e

    def test_unclosed_call(self):
        with self.assertRaises(PrematureEOFError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('print(a + 3').value).parse().error
            if e: raise e

    def test_ml_unclosed_call(self):
        with self.assertRaises(PrematureEOFError):
            text = ':add [a b] <~ a + b\nx = add(1'
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_unclosed_atom(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('(a + 3').value).parse().error
            if e: raise e

    def test_invalid_map_1(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('{1 + * 3 : 2}').value).parse().error
            if e: raise e

    def test_invalid_map_2(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('{1 : }').value).parse().error
            if e: raise e

    def test_invalid_map_3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('{1 . }').value).parse().error
            if e: raise e

    def test_invalid_map_4(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('{1 : 2 ').value).parse().error
            if e: raise e

    def test_invalid_map_5(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('{1 + 2 return}').value).parse().error
            if e: raise e

    def test_invalid_list_1(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('[1 + * 3 2]').value).parse().error
            if e: raise e

    def test_invalid_list_2(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('[1').value).parse().error
            if e: raise e

    def test_invalid_if_1(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==').value).parse().error
            if e: raise e

    def test_invalid_if_2(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1').value).parse().error
            if e: raise e

    def test_invalid_if_3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:').value).parse().error
            if e: raise e

    def test_invalid_if_4(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1\n{').value).parse().error
            if e: raise e

    def test_invalid_if_5(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1\n{1+').value).parse().error
            if e: raise e

    def test_invalid_if_6(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1\n{1+2]').value).parse().error
            if e: raise e

    def test_invalid_if_7(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1 {3}').value).parse().error
            if e: raise e

    def test_invalid_if_8(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1 {3').value).parse().error
            if e: raise e

    def test_invalid_elif_1(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n!? 1==').value).parse().error
            if e: raise e

    def test_invalid_elif_2(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n!? 1==1').value).parse().error
            if e: raise e

    def test_invalid_elif_3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n!? 1==1:').value).parse().error
            if e: raise e

    def test_invalid_elif_4(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n!? 1==1\n{').value).parse().error
            if e: raise e

    def test_invalid_elif_5(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n!? 1==1\n{1+').value).parse().error
            if e: raise e

    def test_invalid_elif_6(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n!? 1==1\n{1+2]').value).parse().error
            if e: raise e

    def test_invalid_else_1(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n! 1').value).parse().error
            if e: raise e

    def test_invalid_else_2(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n!: 1==').value).parse().error
            if e: raise e

    def test_invalid_else_3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n! 1==1:').value).parse().error
            if e: raise e

    def test_invalid_else_4(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n! :\n{').value).parse().error
            if e: raise e

    def test_invalid_else_5(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n!{1+').value).parse().error
            if e: raise e

    def test_invalid_else_6(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n! {\n1+2]').value).parse().error
            if e: raise e

    def test_invalid_else_7(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('? 1==1:1\n!{1+2}').value).parse().error
            if e: raise e

    def test_invalid_for_1(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for 123').value).parse().error
            if e: raise e

    def test_invalid_for_2(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a *').value).parse().error
            if e: raise e

    def test_invalid_for_3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 3+').value).parse().error
            if e: raise e

    def test_invalid_for_4(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 . ').value).parse().error
            if e: raise e

    def test_invalid_for_5(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 .. 2+ ').value).parse().error
            if e: raise e

    def test_invalid_for_6(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 .. 2 .. ').value).parse().error
            if e: raise e

    def test_invalid_for_7(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 .. 2 .. 3=').value).parse().error
            if e: raise e

    def test_invalid_for_8(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 .. 2 .. 3 : i+').value).parse().error
            if e: raise e

    def test_invalid_for_9(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 .. 2 .. 3 {').value).parse().error
            if e: raise e

    def test_invalid_for_10(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 .. 2 .. 3 {\n1+').value).parse().error
            if e: raise e

    def test_invalid_for_11(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 .. 2 .. 3 {\n1+1').value).parse().error
            if e: raise e

    def test_invalid_for_12(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 2 .. 3 {\n1+1}').value).parse().error
            if e: raise e

    def test_invalid_for_13(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('for a = 1 .. 2 3 {\n1+1}').value).parse().error
            if e: raise e

    def test_invalid_foreach_1(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach 123').value).parse().error
            if e: raise e

    def test_invalid_foreach_2(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a').value).parse().error
            if e: raise e

    def test_invalid_foreach_3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a in').value).parse().error
            if e: raise e

    def test_invalid_foreach_4(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a in 123').value).parse().error
            if e: raise e

    def test_invalid_foreach_5(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a in [1 2 3]').value).parse().error
            if e: raise e

    def test_invalid_foreach_6(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a in [1 2 3]\ni = 1').value).parse().error
            if e: raise e

    def test_invalid_foreach_7(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a in [1 2 3] : i =').value).parse().error
            if e: raise e

    def test_invalid_foreach_8(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a in [1 2 3] { i = }').value).parse().error
            if e: raise e

    def test_invalid_foreach_9(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a in [1 2 3] {\ni = }').value).parse().error
            if e: raise e

    def test_invalid_foreach_10(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a in [1 2 3] {\ni = 1').value).parse().error
            if e: raise e

    def test_invalid_foreach_11(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('foreach a in [1 2 3] {\ni = 1]').value).parse().error
            if e: raise e

    def test_invalid_while_1(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while .').value).parse().error
            if e: raise e

    def test_invalid_while_2(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while 1+').value).parse().error
            if e: raise e

    def test_invalid_while_3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while 1:').value).parse().error
            if e: raise e

    def test_invalid_while_4(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while 1: 1+').value).parse().error
            if e: raise e

    def test_invalid_while_5(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while 1: 1+1 .').value).parse().error
            if e: raise e

    def test_invalid_while_6(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while 1 {\n1+').value).parse().error
            if e: raise e

    def test_invalid_while_7(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while 1 {\n1+2').value).parse().error
            if e: raise e

    def test_invalid_while_8(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while 1 {\n1+2]').value).parse().error
            if e: raise e

    def test_invalid_while_9(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while 1 {1+2}').value).parse().error
            if e: raise e

    def test_invalid_while_10(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('while 1==1').value).parse().error
            if e: raise e

    def test_invalid_when_1(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when .').value).parse().error
            if e: raise e

    def test_invalid_when_2(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when 1+').value).parse().error
            if e: raise e

    def test_invalid_when_3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when 1:').value).parse().error
            if e: raise e

    def test_invalid_when_4(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when 1: 1+').value).parse().error
            if e: raise e

    def test_invalid_when_5(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when 1: 1+1 .').value).parse().error
            if e: raise e

    def test_invalid_when_6(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when 1 {\n1+').value).parse().error
            if e: raise e

    def test_invalid_when_7(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when 1 {\n1+2').value).parse().error
            if e: raise e

    def test_invalid_when_8(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when 1 {\n1+2]').value).parse().error
            if e: raise e

    def test_invalid_when_9(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when 1 {1+2}').value).parse().error
            if e: raise e

    def test_invalid_when_10(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('when 1==1').value).parse().error
            if e: raise e

    def test_invalid_func_1(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(':add [').value).parse().error
            if e: raise e

    def test_invalid_func_2(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(':add ]').value).parse().error
            if e: raise e

    def test_invalid_func_3(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(':add <~ 1 + 1').value).parse().error
            if e: raise e

    def test_invalid_func_4(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(': [').value).parse().error
            if e: raise e

    def test_invalid_func_5(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(': ]').value).parse().error
            if e: raise e

    def test_invalid_func_6(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(': <~ 1 + 1').value).parse().error
            if e: raise e

    def test_invalid_func_7(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(': add [] 1 + 1').value).parse().error
            if e: raise e

    def test_invalid_func_8(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(': add [] <~ {1 + 1}').value).parse().error
            if e: raise e

    def test_invalid_struct_1(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('::add [').value).parse().error
            if e: raise e

    def test_invalid_struct_2(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('::add ]').value).parse().error
            if e: raise e

    def test_invalid_struct_3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize('::add <~ 1 + 1').value).parse().error
            if e: raise e

    def test_invalid_struct_4(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(':: [').value).parse().error
            if e: raise e

    def test_invalid_struct_5(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(':: ]').value).parse().error
            if e: raise e

    def test_invalid_struct_6(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(':: <~ 1 + 1').value).parse().error
            if e: raise e

    def test_invalid_struct_7(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(':: add [] 1 + 1').value).parse().error
            if e: raise e

    def test_invalid_struct_8(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(':: add [] <~ {1 + 1}').value).parse().error
            if e: raise e

    def test_invalid_interface_1(self):
        with self.assertRaises(UnclosedScopeError):
            text = ':: mytype [x y] {\na = x\ny = b\n.\n}'
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_interface_2(self):
        with self.assertRaises(UnclosedScopeError):
            text = ':: mytype [x y] {\na = x\ny = b\n.add\n}'
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_interface_3(self):
        with self.assertRaises(UnclosedScopeError):
            text = ':: mytype [x y] {\na = x\ny = b\n.add =\n}'
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_interface_4(self):
        with self.assertRaises(UnclosedScopeError):
            text = ':: mytype [x y] {\na = x\ny = b\n.add <~\n}'
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_interface_5(self):
        with self.assertRaises(UnclosedScopeError):
            text = ':: mytype [x y] {\na = x\ny = b\n.add <~ z+\n}'
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try1(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry a=a/1\ncatch:a=a*3'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try2(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry: a=\nuse:a=a*3'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try3(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry: a=a/1\nuse:a=a*3'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try4(self):
        with self.assertRaises(UnopenedScopeError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry: a=a/1\ncatch a=a*3'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try5(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry{ a=a/1\ncatch a=a*3'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try6(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry{\na=a/1\ncatch a=a*3'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try7(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry{\na=a/1}\ncatch{ a=a*3'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try8(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry{\na=a/1}\ncatch{\na=a*3'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try9(self):
        with self.assertRaises(InvalidSyntaxError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry{\na=a/1}\ncatch{\na='
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_invalid_try10(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            text = 'a=1\ntry{\na=a/1}\ncatch{\na=1]'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_func_no_right_bracket(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            text = ': a [ b c'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_struct_no_right_bracket(self):
        with self.assertRaises(UnclosedScopeError):
            context.symbol_table = get_sym_table()
            text = ':: a [ b c'
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e

    def test_function_return_not_last(self):
        with self.assertRaises(InvalidSyntaxError):
            text = ':add [a b] <~ {\nn = a + b\nreturn n\nn = b + a\nx = add(1)'
            context.symbol_table = get_sym_table()
            e = Parser(Lexer().tokenize(text).value).parse().error
            if e: raise e
