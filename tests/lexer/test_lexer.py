import unittest

from safyr.interpreter import *
from safyr.lexer import *
from safyr.parser import *


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


class TestLexerErrors(unittest.TestCase):

    def test_letter_after_int(self):
        with self.assertRaises(IllegalTokenFormatError):
            e = Lexer().tokenize('1a').error
            if e: raise e

    def test_punc_after_int(self):
        with self.assertRaises(IllegalTokenFormatError):
            e = Lexer().tokenize('1_').error
            if e: raise e

    def test_letter_after_flt(self):
        with self.assertRaises(IllegalTokenFormatError):
            e = Lexer().tokenize('1.0a').error
            if e: raise e

    def test_punc_after_flt(self):
        with self.assertRaises(IllegalTokenFormatError):
            e = Lexer().tokenize('1.0_').error
            if e: raise e

    def test_punc_after_sym(self):
        with self.assertRaises(IllegalTokenFormatError):
            e = Lexer().tokenize('a_').error
            if e: raise e

    def test_singlequote_after_sym(self):
        with self.assertRaises(IllegalTokenFormatError):
            e = Lexer().tokenize("a_'").error
            if e: raise e

    def test_doublequote_after_sym(self):
        with self.assertRaises(IllegalTokenFormatError):
            e = Lexer().tokenize('a"').error
            if e: raise e

    def test_illegal_char(self):
        with self.assertRaises(IllegalInputCharacterError):
            e = Lexer().tokenize('`').error
            if e: raise e

    def test_unclosed_single_quote_begin(self):
        with self.assertRaises(UnmatchedQuoteError):
            e = Lexer().tokenize("'hello").error
            if e: raise e

    def test_unclosed_double_quote_begin(self):
        with self.assertRaises(UnmatchedQuoteError):
            e = Lexer().tokenize('"hello').error
            if e: raise e

    def test_unclosed_single_quote_with_newline(self):
        with self.assertRaises(UnmatchedQuoteError):
            e = Lexer().tokenize("'hello\n").error
            if e: raise e

    def test_unclosed_double_quote_with_newline(self):
        with self.assertRaises(UnmatchedQuoteError):
            e = Lexer().tokenize('"hello\n').error
            if e: raise e

    def test_unclosed_single_quote_end(self):
        with self.assertRaises(UnmatchedQuoteError):
            e = Lexer().tokenize("'").error
            if e: raise e

    def test_unclosed_double_quote_end(self):
        with self.assertRaises(UnmatchedQuoteError):
            e = Lexer().tokenize('"').error
            if e: raise e


class TestLexerBasicTokens(unittest.TestCase):

    # test that each individual token is recognized correctly
    def test_empty_string(self):
        self.assertEqual(Lexer().tokenize('').value, [BRK])

    def test_basic_comment(self):
        self.assertEqual(Lexer().tokenize('; comment').value, [BRK])

    def test_basic_int(self):
        self.assertEqual(Lexer().tokenize('1').value, [Token('INT', 1), BRK])

    def test_basic_flt(self):
        self.assertEqual(Lexer().tokenize('1.0').value, [Token('FLT', 1.), BRK])

    def test_basic_sym(self):
        self.assertEqual(Lexer().tokenize('a').value, [Token('SYM', 'a'), BRK])

    def test_empty_st1(self):
        self.assertEqual(Lexer().tokenize('""').value, [Token('STR', ''), BRK])

    def test_empty_st2(self):
        self.assertEqual(Lexer().tokenize("''").value, [Token('FSTR', ''), BRK])

    def test_basic_st1(self):
        self.assertEqual(Lexer().tokenize('"a"').value, [Token('STR', 'a'), BRK])

    def test_basic_st2(self):
        self.assertEqual(Lexer().tokenize("'a'").value, [Token('FSTR', 'a'), BRK])

    def test_basic_pls(self):
        self.assertEqual(Lexer().tokenize('+').value, [Token('PLS', '+'), BRK])

    def test_basic_mns(self):
        self.assertEqual(Lexer().tokenize('-').value, [Token('MNS', '-'), BRK])

    def test_basic_mul(self):
        self.assertEqual(Lexer().tokenize('*').value, [Token('MUL', '*'), BRK])

    def test_basic_div(self):
        self.assertEqual(Lexer().tokenize('/').value, [Token('DIV', '/'), BRK])

    def test_basic_mod(self):
        self.assertEqual(Lexer().tokenize('%').value, [Token('MOD', '%'), BRK])

    def test_basic_pow(self):
        self.assertEqual(Lexer().tokenize('^').value, [Token('POW', '^'), BRK])

    def test_basic_lt(self):
        self.assertEqual(Lexer().tokenize('<').value, [Token('LT', '<'), BRK])

    def test_basic_gt(self):
        self.assertEqual(Lexer().tokenize('>').value, [Token('GT', '>'), BRK])

    def test_basic_and(self):
        self.assertEqual(Lexer().tokenize('&').value, [Token('AND', '&'), BRK])

    def test_basic_or(self):
        self.assertEqual(Lexer().tokenize('|').value, [Token('OR', '|'), BRK])

    def test_basic_not(self):
        self.assertEqual(Lexer().tokenize('~').value, [Token('NOT', '~'), BRK])

    def test_basic_assign(self):
        self.assertEqual(Lexer().tokenize('=').value, [Token('ASG', '='), BRK])

    # test that each 2-char token is recognized correctly
    def test_basic_plseq(self):
        self.assertEqual(Lexer().tokenize('+=').value, [Token('ASG', '+='), BRK])

    def test_basic_mnseq(self):
        self.assertEqual(Lexer().tokenize('-=').value, [Token('ASG', '-='), BRK])

    def test_basic_muleq(self):
        self.assertEqual(Lexer().tokenize('*=').value, [Token('ASG', '*='), BRK])

    def test_basic_diveq(self):
        self.assertEqual(Lexer().tokenize('/=').value, [Token('ASG', '/='), BRK])

    def test_basic_modeq(self):
        self.assertEqual(Lexer().tokenize('%=').value, [Token('ASG', '%='), BRK])

    def test_basic_poweq(self):
        self.assertEqual(Lexer().tokenize('^=').value, [Token('ASG', '^='), BRK])

    def test_basic_constasg(self):
        self.assertEqual(Lexer().tokenize(':=').value, [Token('ASG', ':='), BRK])

    def test_basic_le(self):
        self.assertEqual(Lexer().tokenize('<=').value, [Token('LE', '<='), BRK])

    def test_basic_ge(self):
        self.assertEqual(Lexer().tokenize('>=').value, [Token('GE', '>='), BRK])

    def test_basic_eq(self):
        self.assertEqual(Lexer().tokenize('==').value, [Token('EQ', '=='), BRK])

    def test_basic_ne(self):
        self.assertEqual(Lexer().tokenize('!=').value, [Token('NE', '!='), BRK])

    def test_basic_nand(self):
        self.assertEqual(Lexer().tokenize('~&').value, [Token('NAND', '~&'), BRK])

    def test_basic_nor(self):
        self.assertEqual(Lexer().tokenize('~|').value, [Token('NOR', '~|'), BRK])

    def test_basic_xor(self):
        self.assertEqual(Lexer().tokenize('><').value, [Token('XOR', '><'), BRK])

    def test_basic_inj(self):
        self.assertEqual(Lexer().tokenize('<~').value, [Token('INJ', '<~'), BRK])

    def test_basic_ret(self):
        self.assertEqual(Lexer().tokenize('~>').value, [Token('IN', '~>'), BRK])

    def test_basic_getlistleft(self):
        self.assertEqual(Lexer().tokenize('</').value, [Token('LSLC', '</'), BRK])

    def test_basic_getlistright(self):
        self.assertEqual(Lexer().tokenize('/>').value, [Token('RSLC', '/>'), BRK])


class TestLexerWhitespaceIgnore(unittest.TestCase):

    # test to ensure that whitespace gets left out entirely except for line breaks
    def test_onespace(self):
        self.assertEqual(Lexer().tokenize(' ').value, [BRK])

    def test_twospaces(self):
        self.assertEqual(Lexer().tokenize('  ').value, [BRK])

    def test_tab(self):
        self.assertEqual(Lexer().tokenize('\t').value, [BRK])

    def test_newline(self):
        self.assertEqual(Lexer().tokenize('\n').value, [Token('BREAK', None), BRK])

    def test_int_leadingspace(self):
        self.assertEqual(Lexer().tokenize(' 1').value, [Token('INT', 1), BRK])

    def test_int_trailingspace(self):
        self.assertEqual(Lexer().tokenize('1 ').value, [Token('INT', 1), BRK])

    def test_flt_leadingspace(self):
        self.assertEqual(Lexer().tokenize(' 1.').value, [Token('FLT', 1.), BRK])

    def test_flt_trailingspace(self):
        self.assertEqual(Lexer().tokenize('1. ').value, [Token('FLT', 1.), BRK])

    def test_sym_leadingspace(self):
        self.assertEqual(Lexer().tokenize(' a').value, [Token('SYM', 'a'), BRK])

    def test_sym_trailingspace(self):
        self.assertEqual(Lexer().tokenize('a ').value, [Token('SYM', 'a'), BRK])

    def test_newline_between_tokens(self):
        self.assertEqual(Lexer().tokenize('1\n1').value, [Token('INT', 1),
                                                    Token('BREAK', None),
                                                    Token('INT', 1),
                                                    BRK])


class TestLexerEqSplitting(unittest.TestCase):

    # ensure that operators involving '=' are recognized correctly
    def test_eq_1(self):
        self.assertEqual(Lexer().tokenize('===').value,
                         [Token('EQ', '=='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_2(self):
        self.assertEqual(Lexer().tokenize('= ==').value,
                         [Token('ASG', '='),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_3(self):
        self.assertEqual(Lexer().tokenize('====').value,
                         [Token('EQ', '=='),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_4(self):
        self.assertEqual(Lexer().tokenize('!==').value,
                         [Token('NE', '!='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_5(self):
        self.assertEqual(Lexer().tokenize('<==').value,
                         [Token('LE', '<='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_6(self):
        self.assertEqual(Lexer().tokenize('>==').value,
                         [Token('GE', '>='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_7(self):
        self.assertEqual(Lexer().tokenize('< ==').value,
                         [Token('LT', '<'),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_8(self):
        self.assertEqual(Lexer().tokenize('> ==').value,
                         [Token('GT', '>'),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_9(self):
        self.assertEqual(Lexer().tokenize('+==').value,
                         [Token('ASG', '+='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_10(self):
        self.assertEqual(Lexer().tokenize('+ ==').value,
                         [Token('PLS', '+'),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_11(self):
        self.assertEqual(Lexer().tokenize('-==').value,
                         [Token('ASG', '-='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_12(self):
        self.assertEqual(Lexer().tokenize('- ==').value,
                         [Token('MNS', '-'),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_13(self):
        self.assertEqual(Lexer().tokenize('*==').value,
                         [Token('ASG', '*='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_14(self):
        self.assertEqual(Lexer().tokenize('* ==').value,
                         [Token('MUL', '*'),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_15(self):
        self.assertEqual(Lexer().tokenize('/==').value,
                         [Token('ASG', '/='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_16(self):
        self.assertEqual(Lexer().tokenize('/ ==').value,
                         [Token('DIV', '/'),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_17(self):
        self.assertEqual(Lexer().tokenize('%==').value,
                         [Token('ASG', '%='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_18(self):
        self.assertEqual(Lexer().tokenize('% ==').value,
                         [Token('MOD', '%'),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_19(self):
        self.assertEqual(Lexer().tokenize('^==').value,
                         [Token('ASG', '^='),
                          Token('ASG', '='),
                          BRK])

    def test_eq_20(self):
        self.assertEqual(Lexer().tokenize('^ ==').value,
                         [Token('POW', '^'),
                          Token('EQ', '=='),
                          BRK])

    def test_eq_21(self):
        self.assertEqual(Lexer().tokenize('=%').value,
                         [Token('ASG', '='),
                          Token('MOD', '%'),
                          BRK])

    def test_eq_22(self):
        self.assertEqual(Lexer().tokenize('="A"').value,
                         [Token('ASG', '='),
                          Token('STR', 'A'),
                          BRK])

    def test_eq_22(self):
        self.assertEqual(Lexer().tokenize("='A'").value,
                         [Token('ASG', '='),
                          Token('FSTR', 'A'),
                          BRK])


class TestLexerConsecutiveTokenParsing(unittest.TestCase):

    def test_dots_and_nums_1(self):
        self.assertEqual(Lexer().tokenize('..2').value,
                         [Token('OPS', '..'),
                          Token('INT', 2),
                          BRK])

    def test_dots_and_nums_2(self):
        self.assertEqual(Lexer().tokenize('...2').value,
                         [Token('OPS', '..'),
                          Token('FLT', .2),
                          BRK])

    def test_dots_and_nums_3(self):
        self.assertEqual(Lexer().tokenize('. 2').value,
                         [Token('DOT', '.'),
                          Token('INT', 2),
                          BRK])

    def test_dots_and_nums_4(self):
        self.assertEqual(Lexer().tokenize('.. 2').value,
                         [Token('OPS', '..'),
                          Token('INT', 2),
                          BRK])

    def test_dots_and_nums_5(self):
        self.assertEqual(Lexer().tokenize('2 .').value,
                         [Token('INT', 2),
                          Token('DOT', '.'),
                          BRK])

    def test_dots_and_nums_6(self):
        self.assertEqual(Lexer().tokenize('2. .').value,
                         [Token('FLT', 2.),
                          Token('DOT', '.'),
                          BRK])

    def test_dots_and_nums_7(self):
        self.assertEqual(Lexer().tokenize('2..').value,
                         [Token('FLT', 2.),
                          Token('DOT', '.'),
                          BRK])

    def test_dots_and_nums_8(self):
        self.assertEqual(Lexer().tokenize('2...').value,
                         [Token('FLT', 2.),
                          Token('OPS', '..'),
                          BRK])

    def test_dots_and_nums_9(self):
        self.assertEqual(Lexer().tokenize('.2.').value,
                         [Token('FLT', .2),
                          Token('DOT', '.'),
                          BRK])

    def test_dots_and_nums_10(self):
        self.assertEqual(Lexer().tokenize('.2..').value,
                         [Token('FLT', .2),
                          Token('OPS', '..'),
                          BRK])

    def test_dots_and_nums_11(self):
        self.assertEqual(Lexer().tokenize('.2. .').value,
                         [Token('FLT', .2),
                          Token('DOT', '.'),
                          Token('DOT', '.'),
                          BRK])

    def test_consecutive_nots(self):
        self.assertEqual(Lexer().tokenize('~~').value,
                         [Token('NOT', '~'),
                          Token('NOT', '~'),
                          BRK])

    def test_consecutive_singleops(self):
        self.assertEqual(Lexer().tokenize('~[').value,
                         [Token('NOT', '~'),
                          Token('LBR', '['),
                          BRK])