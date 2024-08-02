import unittest

from interpreter import *
from lexer import *
from parser import *


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
context = Context('<test>')


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
        self.assertEqual(Lexer().tokenize("''").value, [Token('STR', ''), BRK])

    def test_basic_st1(self):
        self.assertEqual(Lexer().tokenize('"a"').value, [Token('STR', 'a'), BRK])

    def test_basic_st2(self):
        self.assertEqual(Lexer().tokenize("'a'").value, [Token('STR', 'a'), BRK])

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
                          Token('STR', 'A'),
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

# END LEXER SECTION #

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

# END PARSER SECTION

# BEGIN INTERPRETER SECTION

class TestInterpreterBasicObjects(unittest.TestCase):

    def test_basic_int(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1').value).parse().node,
                                   context).value,
                         Number(1))

    # Need to check the whole t=type thing
    # I have to make sure that hasn't affected any functionality of the program, because
    # I forgot I set it to INT by default, and that messed up this test at first
    def test_basic_flt(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1.').value).parse().node,
                                   context).value,
                         Number(1., t='FLT'))

    def test_empty_str(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('""').value).parse().node,
                                   context).value,
                         String(""))

    def test_basic_str(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"').value).parse().node,
                                   context).value, String("a"))

    def test_empty_list(self):
        result = RUN.visit(Parser(Lexer().tokenize('[]').value).parse().node, context).value
        self.assertEqual(result.elements, [])

    def test_one_element_list(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1]').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(1)])

    def test_two_element_list(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2]').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(1), Number(2)])

    def test_empty_map(self):
        result = RUN.visit(Parser(Lexer().tokenize('{}').value).parse().node, context).value
        self.assertEqual(result.elements, {})

    def test_basic_map(self):
        result = RUN.visit(Parser(Lexer().tokenize('{1: "ab"}').value).parse().node, context).value
        self.assertEqual(result.elements, {Number(1): String("ab")})

    def test_multitype_map(self):
        result = RUN.visit(Parser(Lexer().tokenize('{1: "ab"\n2: "bc"\n"de": 3}').value
                                  ).parse().node, context).value
        self.assertEqual(result.elements, {Number(1): String("ab"),
                                           Number(2): String("bc"),
                                           String("de"): Number(3)})

    def test_delete(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a = 1\n\ndel a').value
                         ).parse().node, context)
        self.assertFalse('a' in context.symbol_table.symbols)


class TestInterpreterVariableAssignment(unittest.TestCase):

    def test_dynint_to_int_dynamic(self):
        text = 'a=1\na = 6'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_labeled_dynint_to_int_dynamic(self):
        text = 'var a=1\na = 6'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_dynint_to_flt_dynamic(self):
        text = 'a=1\na = 6.'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6., t='FLT'))

    def test_labeled_dynint_to_flt_dynamic(self):
        text = 'var a=1\na = 6.'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6., t='FLT'))

    def test_dynint_to_str_dynamic(self):
        text = 'a=1\na = "6"'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], String("6"))

    def test_labeled_dynint_to_str_dynamic(self):
        text = 'var a=1\na = "6"'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], String("6"))

    def test_dynstr_to_int_dynamic(self):
        text = 'a="1"\na = 6'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_labeled_dynstr_to_int_dynamic(self):
        text = 'var a="1"\na = 6'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_dynstr_to_flt_dynamic(self):
        text = 'a="1"\na = 6.'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6., t='FLT'))

    def test_labeled_dynstr_to_flt_dynamic(self):
        text = 'var a="1"\na = 6.'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6., t='FLT'))

    def test_dynstr_to_str_dynamic(self):
        text = 'a="1"\na = "6"'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], String("6"))

    def test_labeled_dynstr_to_str_dynamic(self):
        text = 'var a="1"\na = "6"'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], String("6"))

    def test_stcint_to_int_static(self):
        text = 'a=1\na = 6'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_labeled_stcint_to_int_static(self):
        text = 'int a=1\na = 6'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_stcint_to_flt_static(self):
        text = 'a=1\na = 6.'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_labeled_stcint_to_flt_static(self):
        text = 'int a=1\na = 6.'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_stcflt_to_int_static(self):
        text = 'a=1.\na = 6'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6., t='FLT'))

    def test_labeled_stcflt_to_int_static(self):
        text = 'flt a=1.\na = 6'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6., t='FLT'))

    def test_stcflt_to_flt_static(self):
        text = 'a=1.\na = 6.'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6., t='FLT'))

    def test_labeled_stcflt_to_flt_static(self):
        text = 'flt a=1.\na = 6.'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6., t='FLT'))

    def test_mixed_typing_dynamic(self):
        text = 'int a=1\nb="abc"\na = 6\nb=5'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['b'], Number(5))

    def test_mixed_labeled_typing_dynamic(self):
        text = 'int a=1\nvar b="abc"\na = 6\nb=5'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['b'], Number(5))

    def test_mixed_typing_static(self):
        text = 'a=1\nvar b="abc"\na = 6\nb=5'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['b'], Number(5))

    def test_mixed_labeled_typing_static(self):
        text = 'int a=1\nvar b="abc"\na = 6\nb=5'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['b'], Number(5))

    def test_stcint_fltinput(self):
        text = 'int a = 1.'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(1))

    def test_stcflt_intinput(self):
        text = 'flt a = 1'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(1., t="FLT"))


class TestInterpreterStringOperations(unittest.TestCase):

    def test_string_addition(self):
        result = RUN.visit(Parser(Lexer().tokenize('"ab" + "c"').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("abc"))

    def test_string_sub_noinstance(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abc" - "d"').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("abc"))

    def test_string_sub_oneinstance(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abc" - "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("ac"))

    def test_string_sub_multipleinstances(self):
        result = RUN.visit(Parser(Lexer().tokenize('"babcb" - "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("ac"))

    def test_string_mul(self):
        result = RUN.visit(Parser(Lexer().tokenize('"ab" * 3').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("ababab"))

    def test_string_mulzero(self):
        result = RUN.visit(Parser(Lexer().tokenize('"ab" * 0').value
                                  ).parse().node, context).value
        self.assertEqual(result, String(""))

    def test_string_div(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abc" / "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result, List([String('a'), String('c')]))

    def test_string_div_noinstances(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abc" / "d"').value
                                  ).parse().node, context).value
        self.assertEqual(result, List([String('abc')]))

    def test_string_div_twoinstances(self):
        result = RUN.visit(Parser(Lexer().tokenize('"aabcbaa" / "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result, List([String('aa'), String('c'), String('aa')]))

    def test_string_div_substring(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abcdefg" / "cde"').value
                                  ).parse().node, context).value
        self.assertEqual(result, List([String('ab'), String('fg')]))

    def test_string_div_consecutive_occurrences(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abbcbbd" / "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result, List([String('a'), String('c'), String('d')]))

    def test_string_at(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abc"@1').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("b"))

    def test_string_at_reverse(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abc"@(-1)').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("c"))

    def test_string_lslice(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abcde" </ 2').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("ab"))

    def test_string_lslice_outofbounds(self):
        result = RUN.visit(Parser(Lexer().tokenize('"ab" </ 5').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("ab"))

    def test_string_rslice(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abcde" /> 2').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("de"))

    def test_string_rslice_outofbounds(self):
        result = RUN.visit(Parser(Lexer().tokenize('"ab" /> 5').value
                                  ).parse().node, context).value
        self.assertEqual(result, String("ab"))

    def test_list_contains_true(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abc" ~> "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result, Number(1))

    def test_list_contains_false(self):
        result = RUN.visit(Parser(Lexer().tokenize('"abc" ~> "f"').value
                                  ).parse().node, context).value
        self.assertEqual(result, Number(0))

    def test_int_at(self):
        result = RUN.visit(Parser(Lexer().tokenize('123@1').value
                                  ).parse().node, context).value
        self.assertEqual(result, Number(2))

    def test_int_at_reverse(self):
        result = RUN.visit(Parser(Lexer().tokenize('123@(-1)').value
                                  ).parse().node, context).value
        self.assertEqual(result, Number(3))


class TestInterpreterListOperations(unittest.TestCase):

    def test_list_with_string(self):
        result = RUN.visit(Parser(Lexer().tokenize('["string"]').value).parse().node, context).value
        self.assertEqual(result.elements, [String("string")])

    def test_list_with_two_strings(self):
        result = RUN.visit(Parser(Lexer().tokenize('["s1" "s2"]').value).parse().node, context).value
        self.assertEqual(result.elements, [String("s1"), String("s2")])

    def test_list_different_types(self):
        result = RUN.visit(Parser(Lexer().tokenize('["s1" 1]').value).parse().node, context).value
        self.assertEqual(result.elements, [String("s1"), Number(1)])

    def test_nested_list(self):
        result = RUN.visit(Parser(Lexer().tokenize('[[1 2]]').value).parse().node, context).value
        self.assertEqual(result.elements, [List([Number(1), Number(2)])])

    def test_nested_twolists(self):
        result = RUN.visit(Parser(Lexer().tokenize('[[1 2] [3 4]]').value).parse().node, context).value
        self.assertEqual(result.elements, [List([Number(1), Number(2)]),
                                           List([Number(3), Number(4)])])

    def test_list_addition_int(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2] + 3').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(1), Number(2), Number(3)])

    def test_list_addition_str(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2] + "3"').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(1), Number(2), String("3")])

    def test_list_subtraction_oneinstance(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2 3] - 3').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(1), Number(2)])

    def test_list_subtraction_multipleinstances(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 3 2 3 3 3] - 3').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(1), Number(2)])

    def test_list_at(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2 3]@1').value).parse().node, context).value
        self.assertEqual(result, Number(2))

    def test_list_at_reverse(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2 3]@(-1)').value).parse().node, context).value
        self.assertEqual(result, Number(3))

    def test_list_lslice(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2 3 4 5] </ 2').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(1), Number(2)])

    def test_list_lslice_outofbounds(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2] </ 5').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(1), Number(2)])

    def test_list_rslice(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2 3 4 5] /> 2').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(4), Number(5)])

    def test_list_rslice_outofbounds(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2] /> 5').value).parse().node, context).value
        self.assertEqual(result.elements, [Number(1), Number(2)])

    def test_list_inj(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2] <~ [3 4]').value).parse().node, context).value
        self.assertEqual(result, List([Number(1), Number(2), Number(3), Number(4)]))

    def test_list_mul(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2] * [3 4]').value).parse().node, context).value
        self.assertEqual(result.elements, [List([Number(1), Number(3)]),
                                           List([Number(2), Number(4)])])

    def test_list_div_equalsizes(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2 3 4] / 2').value).parse().node, context).value
        self.assertEqual(result.elements, [List([Number(1), Number(2)]),
                                           List([Number(3), Number(4)])])

    def test_list_div_unequalsizes(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2 3 4] / 3').value).parse().node, context).value
        self.assertEqual(result.elements, [List([Number(1), Number(2), Number(3)]),
                                           List([Number(4)])])

    def test_list_pow_equalsizes(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2] ^ [3 4]').value).parse().node, context).value
        self.assertEqual(result.elements, [List([Number(1), Number(3)]),
                                           List([Number(1), Number(4)]),
                                           List([Number(2), Number(3)]),
                                           List([Number(2), Number(4)])])

    def test_list_pow_unequalsizes(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2 3] ^ [4 5]').value).parse().node, context).value
        self.assertEqual(result.elements, [List([Number(1), Number(4)]),
                                           List([Number(1), Number(5)]),
                                           List([Number(2), Number(4)]),
                                           List([Number(2), Number(5)]),
                                           List([Number(3), Number(4)]),
                                           List([Number(3), Number(5)])])

    def test_list_modify_element(self):
        text = 'a = [1 2 3]\na @ 2 = 59'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['a']
        self.assertEqual(a.elements[2], Number(59))

    def test_list_modify_element_with_left_expr(self):
        text = 'a = [1 2 3]\na @ (1 + 1) = 59'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['a']
        self.assertEqual(a.elements[2], Number(59))

    def test_list_access_with_right_expr(self):
        text = 'a = [1 2 7]\nb = a @ (1 + 1)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        b = context.symbol_table.symbols['b']
        self.assertEqual(b, Number(7))

    def test_list_access_precedence_with_right_expr(self):
        text = 'a = [1 2 7]\nb = a @ 1 + 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        b = context.symbol_table.symbols['b']
        self.assertEqual(b, Number(3))

    def test_list_contains_true(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2] ~> 2').value).parse().node, context).value
        self.assertEqual(result, Number(1))

    def test_list_contains_false(self):
        result = RUN.visit(Parser(Lexer().tokenize('[1 2] ~> 5').value).parse().node, context).value
        self.assertEqual(result, Number(0))


class TestInterpreterMapOperations(unittest.TestCase):

    # + - ~> == !=
    def test_map_add_one(self):
        result = RUN.visit(Parser(Lexer().tokenize('{"a": 1} + {"b": 2}').value
                                  ).parse().node, context).value
        self.assertEqual(result.elements, {String("a"): Number(1),
                                           String("b"): Number(2)})

    def test_map_add_two(self):
        result = RUN.visit(Parser(Lexer().tokenize('{"a": 1} + {"b": 2 "c": 3}').value
                                  ).parse().node, context).value
        self.assertEqual(result.elements, {String("a"): Number(1),
                                           String("b"): Number(2),
                                           String("c"): Number(3)})

    def test_map_add_overwrite(self):
        result = RUN.visit(Parser(Lexer().tokenize('{"a": 1} + {"a": 2 "b": 3}').value
                                  ).parse().node, context).value
        self.assertEqual(result.elements, {String("a"): Number(2),
                                           String("b"): Number(3)})

    def test_map_sub_present(self):
        result = RUN.visit(Parser(Lexer().tokenize('{"a": 1 "b": 2} - "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result.elements, {String("a"): Number(1)})

    def test_map_sub_notpresent(self):
        result = RUN.visit(Parser(Lexer().tokenize('{"a": 1} - "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result.elements, {String("a"): Number(1)})

    def test_map_contains_present(self):
        result = RUN.visit(Parser(Lexer().tokenize('{"a": 1 "b": 2} ~> "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result, Number(1))

    def test_map_contains_notpresent(self):
        result = RUN.visit(Parser(Lexer().tokenize('{"a": 1} ~> "b"').value
                                  ).parse().node, context).value
        self.assertEqual(result, Number(0))

    def test_map_at_present(self):
        result = RUN.visit(Parser(Lexer().tokenize('{"a": 1} @ "a"').value
                                  ).parse().node, context).value
        self.assertEqual(result, Number(1))

    # needs to go to error testing section because it throws invalid syntax
    # def test_map_at_notpresent(self):
    #     result = RUN.visit(Parser(Lexer().tokenize('{"a": 1} @ "b"').value
    #                               ).parse().node, context).value
    #     self.assertEqual(result, Number(1))


class TestInterpreterMathExpressions(unittest.TestCase):

    def test_negative_number(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('-1').value).parse().node,
                                   context).value, Number(-1))

    # basic binary operations
    def test_addition(self):
        result = RUN.visit(Parser(Lexer().tokenize('1+1').value).parse().node, context).value
        self.assertEqual(result, Number(2))

    def test_subtraction(self):
        result = RUN.visit(Parser(Lexer().tokenize('1-1').value).parse().node, context).value
        self.assertEqual(result, Number(0))

    def test_multiplication(self):
        result = RUN.visit(Parser(Lexer().tokenize('1*1').value).parse().node, context).value
        self.assertEqual(result, Number(1))

    def test_division(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1/1').value).parse().node, context).value,
                         Number(1))

    def test_acc_addition(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=1\na += 1').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(2))

    def test_acc_subtraction(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=1\na -= 1').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(0))

    def test_acc_multiplication(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=2\na *= 3').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(6))

    def test_acc_division(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=10\na /= 5').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(2))

    def test_acc_mod(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=7\na %= 5').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(2))

    def test_acc_exp(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=2\na ^= 3').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(8))

    # precedence between pairs of operators
    def test_add_mul_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1+2*3').value).parse().node, context).value,
                         Number(7))

    def test_sub_mul_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1-2*3').value).parse().node, context).value,
                         Number(-5))

    def test_add_div_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1+4/2').value).parse().node, context).value,
                         Number(3))

    def test_sub_div_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1-4/2').value).parse().node, context).value,
                         Number(-1))

    def test_add_mod_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1+4%2').value).parse().node, context).value,
                         Number(1))

    def test_sub_mod_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1-4%2').value).parse().node, context).value,
                         Number(1))

    def test_rev_add_mul_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('2*3+1').value).parse().node, context).value,
                         Number(7))

    def test_rev_sub_mul_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('2*3-1').value).parse().node, context).value,
                         Number(5))

    def test_rev_add_div_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('4/2+1').value).parse().node, context).value,
                         Number(3))

    def test_rev_sub_div_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('4/2-1').value).parse().node, context).value,
                         Number(1))

    def test_rev_add_mod_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('4%2+1').value).parse().node, context).value,
                         Number(1))

    def test_rev_sub_mod_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('4%2-1').value).parse().node, context).value,
                         Number(-1))

    # parentheses control over basic operation precedence
    def test_paren_override1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('(4+2)*3').value).parse().node, context).value,
                         Number(18))

    def test_paren_override2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('4+(2*3)').value).parse().node, context).value,
                         Number(10))

    # testing precedence between exponent and the operator classes above
    def test_pow_add_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('4+2^3').value).parse().node, context).value,
                         Number(12))

    def test_rev_pow_add_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('2^3+4').value).parse().node, context).value,
                         Number(12))

    def test_pow_mul_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('4*2^3').value).parse().node, context).value,
                         Number(32))

    def test_rev_pow_mul_precedence(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('2^3*4').value).parse().node, context).value,
                         Number(32))

    # parentheses control over exponent precedence
    def test_pow_add_paren_override1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('(1+2)^3').value).parse().node, context).value,
                         Number(27))

    def test_pow_paren_override2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('2^(1+2)').value).parse().node, context).value,
                         Number(8))

    def test_pow_mul_paren_override1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('(2*2)^3').value).parse().node, context).value,
                         Number(64))

    def test_pow_mul_paren_override2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('2^(2*3)').value).parse().node, context).value,
                         Number(64))


class TestInterpreterBasicComparators(unittest.TestCase):

    def test_num_eq_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1==1').value).parse().node, context).value,
                                Number(1))

    def test_num_eq_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1==2').value).parse().node, context).value,
                                Number(0))

    def test_num_eq_othertype(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1==[2]').value).parse().node, context).value,
                                Number(0))

    def test_num_ne_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1!=1').value).parse().node, context).value,
                                Number(0))

    def test_num_ne_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1!=2').value).parse().node, context).value,
                                Number(1))

    def test_num_ne_othertype(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1!="a"').value).parse().node, context).value,
                                Number(1))

    def test_num_lt_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1<2').value).parse().node, context).value,
                                Number(1))

    def test_num_lt_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1<0').value).parse().node, context).value,
                                Number(0))

    def test_num_le_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1<=1').value).parse().node, context).value,
                                Number(1))

    def test_num_le_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1<=0').value).parse().node, context).value,
                                Number(0))

    def test_num_gt_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1>0').value).parse().node, context).value,
                                Number(1))

    def test_num_gt_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1>2').value).parse().node, context).value,
                                Number(0))

    def test_num_ge_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1>=0').value).parse().node, context).value,
                                Number(1))

    def test_num_ge_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1>=2').value).parse().node, context).value,
                                Number(0))

    def test_str_eq_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"=="a"').value).parse().node, context).value,
                                Number(1))

    def test_str_eq_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"=="b"').value).parse().node, context).value,
                                Number(0))

    def test_str_eq_othertype(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"==3').value).parse().node, context).value,
                                Number(0))

    def test_str_ne_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"!="a"').value).parse().node, context).value,
                                Number(0))

    def test_str_ne_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"!="b"').value).parse().node, context).value,
                                Number(1))

    def test_str_ne_othertype(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"!=1').value).parse().node, context).value,
                                Number(1))

    def test_str_lt_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"<"b"').value).parse().node, context).value,
                                Number(1))

    def test_str_lt_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"b"<"a"').value).parse().node, context).value,
                                Number(0))

    def test_str_le_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"<="b"').value).parse().node, context).value,
                                Number(1))

    def test_str_le_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"b"<="a"').value).parse().node, context).value,
                                Number(0))

    def test_str_gt_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"b">"a"').value).parse().node, context).value,
                                Number(1))

    def test_str_gt_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a">"b"').value).parse().node, context).value,
                                Number(0))

    def test_str_ge_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"b">="a"').value).parse().node, context).value,
                                Number(1))

    def test_str_ge_false(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a">="b"').value).parse().node, context).value,
                                Number(0))

    def test_lst_eq_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('[1 2]==[1 2]').value).parse().node, context).value,
                                Number(1))

    def test_lst_eq_false_wrongelements(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('[1 2]==[3 4]').value).parse().node, context).value,
                                Number(0))

    def test_lst_eq_false_wrongcardinality(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('[1 2]==[3]').value).parse().node, context).value,
                                Number(0))

    def test_lst_eq_false_wrongtype(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('[1 2]=="a"').value).parse().node, context).value,
                                Number(0))

    def test_lst_ne_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('[1 2]!=[]').value).parse().node, context).value,
                                Number(1))

    def test_lst_ne_false_sameelements(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('[1 2]!=[1 2]').value).parse().node, context).value,
                                Number(0))

    def test_lst_builtineq_true(self):
        return self.assertTrue(List([Number(1), Number(2)]) == List([Number(1), Number(2)]))

    def test_lst_builtineq_false(self):
        return self.assertFalse(List([Number(1), Number(2)]) == List([Number(1), Number(3)]))

    def test_lst_builtineq_false_wrongcardinality(self):
        return self.assertFalse(List([Number(1), Number(2)]) == List([Number(1)]))

    def test_lst_ne_false_wrongtype(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('[1 2]==3').value).parse().node, context).value,
                                Number(0))

    def test_map_eq_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2}=={1: 2}').value).parse().node, context).value,
                                Number(1))

    def test_map_eq_false_wrongelements(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2}=={3: 4}').value).parse().node, context).value,
                                Number(0))

    def test_map_eq_false_wrongcardinality(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2 3: 4}=={3: 4}').value).parse().node, context).value,
                                Number(0))

    def test_map_eq_false_differentkeys(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2}=={3: 2}').value).parse().node, context).value,
                                Number(0))

    def test_map_eq_false_differentvalues(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2}=={1: 3}').value).parse().node, context).value,
                                Number(0))

    def test_map_ne_true(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2}!={1: 2}').value).parse().node, context).value,
                                Number(0))

    def test_map_ne_false_wrongelements(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2}!={3: 4}').value).parse().node, context).value,
                                Number(1))

    def test_map_ne_false_wrongcardinality(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2 3: 4}!={3: 4}').value).parse().node, context).value,
                                Number(1))

    def test_map_ne_false_differentkeys(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2}!={3: 2}').value).parse().node, context).value,
                                Number(1))

    def test_map_ne_false_differentvalues(self):
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('{1: 2}!={1: 3}').value).parse().node, context).value,
                                Number(1))


class TestInterpreterBasicLogicalOperators(unittest.TestCase):

    def test_basic_not_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('~1').value).parse().node,
                                   context).value,
                         Number(0))

    def test_double_not_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('~~1').value).parse().node,
                                   context).value,
                         Number(1))

    def test_basic_not_false(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('~0').value).parse().node,
                                   context).value,
                         Number(1))

    def test_double_not_false(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('~~0').value).parse().node,
                                   context).value,
                         Number(0))

    def test_basic_and_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1&1').value).parse().node,
                                   context).value,
                         Number(1))

    def test_basic_and_false1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1&0').value).parse().node,
                                   context).value,
                         Number(0))

    def test_basic_and_false2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('0&0').value).parse().node,
                                   context).value,
                         Number(0))

    def test_basic_or_true1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1|1').value).parse().node,
                                   context).value,
                         Number(1))

    def test_basic_or_true2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1|0').value).parse().node,
                                   context).value,
                         Number(1))

    def test_basic_or_false(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('0|0').value).parse().node,
                                   context).value,
                         Number(0))

    def test_basic_nand_true1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('0~&1').value).parse().node,
                                   context).value,
                         Number(1))

    def test_basic_nand_true2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('0~&0').value).parse().node,
                                   context).value,
                         Number(1))

    def test_basic_nand_false(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1~&1').value).parse().node,
                                   context).value,
                         Number(0))

    def test_basic_nor_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('0~|0').value).parse().node,
                                   context).value,
                         Number(1))

    def test_basic_nor_false1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1~|0').value).parse().node,
                                   context).value,
                         Number(0))

    def test_basic_nor_false2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1~|1').value).parse().node,
                                   context).value,
                         Number(0))

    def test_basic_xor_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('0><1').value).parse().node,
                                   context).value,
                         Number(1))

    def test_basic_xor_false1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('0><0').value).parse().node,
                                   context).value,
                         Number(0))

    def test_basic_xor_false2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('1><1').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_not_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('~"a"').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_double_not_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('~~"a"').value).parse().node,
                                   context).value,
                         Number(1))

    def test_str_not_false(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('~""').value).parse().node,
                                   context).value,
                         Number(1))

    def test_str_double_not_false(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('~~""').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_and_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"&"a"').value).parse().node,
                                   context).value,
                         Number(1))

    def test_str_and_false1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"&""').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_and_false2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('""&""').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_or_true1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"|"a"').value).parse().node,
                                   context).value,
                         Number(1))

    def test_str_or_true2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"|""').value).parse().node,
                                   context).value,
                         Number(1))

    def test_str_or_false(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('""|""').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_nand_true1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('""~&"a"').value).parse().node,
                                   context).value,
                         Number(1))

    def test_str_nand_true2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('""~&""').value).parse().node,
                                   context).value,
                         Number(1))

    def test_str_nand_false(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"~&"a"').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_nor_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('""~|""').value).parse().node,
                                   context).value,
                         Number(1))

    def test_str_nor_false1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"~|""').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_nor_false2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"~|"a"').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_xor_true(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('""><"a"').value).parse().node,
                                   context).value,
                         Number(1))

    def test_str_xor_false1(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('""><""').value).parse().node,
                                   context).value,
                         Number(0))

    def test_str_xor_false2(self):
        self.assertEqual(RUN.visit(Parser(Lexer().tokenize('"a"><"a"').value).parse().node,
                                   context).value,
                         Number(0))


class TestInterpreterErrors(unittest.TestCase):

    def test_divide_by_0(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 / 0').value).parse().node, context).error
            if e: raise e

    def test_mod_by_0(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 % 0').value).parse().node, context).error
            if e: raise e

    def test_int_at_outofbounds(self):
        with self.assertRaises(OutOfBoundsError):
            e = RUN.visit(Parser(Lexer().tokenize('123@20').value).parse().node, context).error
            if e: raise e

    def test_int_at_othertype(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('123 @"a"').value).parse().node, context).error
            if e: raise e

    def test_add_str_to_num(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 + "a"').value).parse().node, context).error
            if e: raise e

    def test_add_num_to_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" + 1').value).parse().node, context).error
            if e: raise e

    def test_sub_str_to_num(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 - "a"').value).parse().node, context).error
            if e: raise e

    def test_sub_num_to_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" - 1').value).parse().node, context).error
            if e: raise e

    def test_mul_str_to_num(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 * "a"').value).parse().node, context).error
            if e: raise e

    def test_mul_str_to_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" * "a"').value).parse().node, context).error
            if e: raise e

    def test_div_str_to_num(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 / "a"').value).parse().node, context).error
            if e: raise e

    def test_div_num_to_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" / 1').value).parse().node, context).error
            if e: raise e

    def test_str_at_str(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" @ "a"').value).parse().node, context).error
            if e: raise e

    def test_str_at_outofbounds(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" @ 5').value).parse().node, context).error
            if e: raise e

    def test_str_rslice_str(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" /> "a"').value).parse().node, context).error
            if e: raise e

    def test_str_lslice_str(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" </ "a"').value).parse().node, context).error
            if e: raise e

    def test_str_contains_int(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" ~> 1').value).parse().node, context).error
            if e: raise e

    def test_lst_mul_int(self):
        with self.assertRaises(NotImplementedError):
            e = RUN.visit(Parser(Lexer().tokenize('[1 2] * 1').value).parse().node, context).error
            if e: raise e

    def test_lst_mul_lst_wrongsize(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('[1 2] * [1 2 3]').value).parse().node, context).error
            if e: raise e

    def test_lst_div_str(self):
        with self.assertRaises(NotImplementedError):
            e = RUN.visit(Parser(Lexer().tokenize('[1 2] / "a"').value).parse().node, context).error
            if e: raise e

    def test_lst_at_str(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('[1 2] @ "a"').value).parse().node, context).error
            if e: raise e

    def test_lst_at_outofbounds(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('[1 2] @ 5').value).parse().node, context).error
            if e: raise e

    def test_lst_lslice_str(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('[1 2] </ "a"').value).parse().node, context).error
            if e: raise e

    def test_lst_pow_str(self):
        with self.assertRaises(NotImplementedError):
            e = RUN.visit(Parser(Lexer().tokenize('[1 2] ^ "a"').value).parse().node, context).error
            if e: raise e

    def test_lst_inj_str(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('[1 2] <~ "a"').value).parse().node, context).error
            if e: raise e

    def test_map_add_str(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('{1: 2} + "a"').value).parse().node, context).error
            if e: raise e

    def test_map_add_missingkey(self):
        with self.assertRaises(InvalidSyntaxError):
            e = RUN.visit(Parser(Lexer().tokenize('{1: 2} @ "a"').value).parse().node, context).error
            if e: raise e

    def test_mod_str_to_num(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 % "a"').value).parse().node, context).error
            if e: raise e

    def test_mod_num_to_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" % 1').value).parse().node, context).error
            if e: raise e

    def test_pow_str_to_num(self):
        with self.assertRaises(NotImplementedError):
            e = RUN.visit(Parser(Lexer().tokenize('1 ^ "a"').value).parse().node, context).error
            if e: raise e

    def test_pow_num_to_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" ^ 1').value).parse().node, context).error
            if e: raise e

    def test_str_gt_num(self):
        with self.assertRaises(NotImplementedError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" > 1').value).parse().node, context).error
            if e: raise e

    def test_num_gt_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 > "a"').value).parse().node, context).error
            if e: raise e

    def test_str_lt_num(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" < 1').value).parse().node, context).error
            if e: raise e

    def test_num_lt_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 < "a"').value).parse().node, context).error
            if e: raise e

    def test_str_ge_num(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" >= 1').value).parse().node, context).error
            if e: raise e

    def test_num_ge_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 >= "a"').value).parse().node, context).error
            if e: raise e

    def test_str_le_num(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('"a" <= 1').value).parse().node, context).error
            if e: raise e

    def test_num_le_str(self):
        with self.assertRaises(RuntimeError):
            e = RUN.visit(Parser(Lexer().tokenize('1 <= "a"').value).parse().node, context).error
            if e: raise e

    def test_notimplemented_pls(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm + n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_mns(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm - n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_mul(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm * n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_div(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm / n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_pow(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm ^ n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_mod(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm % n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_eq(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm == n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_ne(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm != n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_lt(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm < n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_le(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm <= n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_gt(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm > n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_ge(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm >= n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_and(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm & n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_or(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm | n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_nand(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm ~& n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_nor(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm ~| n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_xor(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm >< n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_at(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm @ n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_contains(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm ~> n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_inj(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm <~ n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_not(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\n'
            text += '~m'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_lslice(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm </ n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_notimplemented_rslice(self):
        with self.assertRaises(NotImplementedError):
            text = '::u [a] {\nx=a}\nm = u(1)\nn = u(2)\n'
            text += 'm /> n'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_overwrite_builtin_variable(self):
        with self.assertRaises(BuiltinViolationError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('T=5').value).parse().node, context).error
            if e: raise e

    def test_overwrite_constant_variable_dynamicmode(self):
        with self.assertRaises(ConstantViolationError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('const a = 5\na=6').value).parse().node, context).error
            if e: raise e

    def test_overwrite_constant_variable_staticmode(self):
        with self.assertRaises(ConstantViolationError):
            context.symbol_table = get_sym_table()
            context.symbol_table.set('static-typing', Number(1))
            e = RUN.visit(Parser(Lexer().tokenize('const a = 5\na=6').value).parse().node, context).error
            if e: raise e

    def test_duplicate_specifier_dynamicmode_dynamicvariable(self):
        with self.assertRaises(InvalidSpecifierError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('var a = 5\nvar a=6').value).parse().node, context).error
            if e: raise e

    def test_duplicate_specifier_dynamicmode_staticvariable(self):
        with self.assertRaises(InvalidSpecifierError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('int a = 5\nint a=6').value).parse().node, context).error
            if e: raise e

    def test_change_type_dynamicmode_staticvariable(self):
        with self.assertRaises(StaticViolationError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('int a = 5\na="6"').value).parse().node, context).error
            if e: raise e

    def test_duplicate_specifier_staticmode_dynamicvariable(self):
        with self.assertRaises(InvalidSpecifierError):
            context.symbol_table = get_sym_table()
            context.symbol_table.set('static-typing', Number(1))
            e = RUN.visit(Parser(Lexer().tokenize('var a = 5\nint a=6').value).parse().node, context).error
            if e: raise e

    def test_duplicate_specifier_staticmode_staticvariable(self):
        with self.assertRaises(InvalidSpecifierError):
            context.symbol_table = get_sym_table()
            context.symbol_table.set('static-typing', Number(1))
            e = RUN.visit(Parser(Lexer().tokenize('int a = 5\nint a=6').value).parse().node, context).error
            if e: raise e

    def test_change_type_staticmode_staticvariable(self):
        with self.assertRaises(StaticViolationError):
            context.symbol_table = get_sym_table()
            context.symbol_table.set('static-typing', Number(1))
            e = RUN.visit(Parser(Lexer().tokenize('a = 5\na="6"').value).parse().node, context).error
            if e: raise e

    def test_uninitialized_variable(self):
        with self.assertRaises(VariableAccessError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = b').value).parse().node, context).error
            if e: raise e

    def test_declaration_error_staticvariable(self):
        with self.assertRaises(StaticViolationError):
            context.symbol_table = get_sym_table()
            context.symbol_table.set('static-typing', Number(1))
            e = RUN.visit(Parser(Lexer().tokenize('int a = "5"').value).parse().node, context).error
            if e: raise e

    def test_when_nonexistent_variable(self):
        with self.assertRaises(VariableAccessError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('when a == 1: a = 5').value).parse().node, context).error
            if e: raise e

    def test_basic_moduleimport_fail(self):
        with self.assertRaises(ModuleImportError):
            text = 'use moduletestfail\na = add(1 2)'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_basic_moduleimport_nonexistent(self):
        with self.assertRaises(ModuleNotFoundError):
            text = 'use nofile\na = add(1 2)'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_function_too_many_args(self):
        with self.assertRaises(InvalidArgumentSetError):
            text = ':add [a b] <~ a + b\nx = add(1 2 3)'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_function_too_few_args(self):
        with self.assertRaises(InvalidArgumentSetError):
            text = ':add [a b] <~ a + b\nx = add(1)'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_open_nonexistent_file(self):
        with self.assertRaises(RuntimeError):
            text = 'open("nofile.txt" "r")'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_dot_wrongtype(self):
        with self.assertRaises(VariableAccessError):
            text = '::mytype [a] {\nx = a\n}\nmyvar = mytype(1)\nmyval = myvar . 1'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_dot_missingproperty(self):
        with self.assertRaises(VariableAccessError):
            text = '::mytype [a] {\nx = a\n}\nmyvar = mytype(1)\nmyval = myvar.y'
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).error
            if e: raise e

    def test_pop_wrongtype1(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = [1 2]\nb = pop(a "a")').value).parse().node, context).error
            if e: raise e

    def test_pop_wrongtype2(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = "a"\nb = pop(a "a")').value).parse().node, context).error
            if e: raise e

    def test_pop_outofbounds(self):
        with self.assertRaises(OutOfBoundsError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = [1 2]\nb = pop(a 5)').value).parse().node, context).error
            if e: raise e

    def test_append_wrongtype(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = "a"\nb = append(a "a")').value).parse().node, context).error
            if e: raise e

    def test_extend_wrongtype1(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = "a"\nb = extend(a "a")').value).parse().node, context).error
            if e: raise e

    def test_extend_wrongtype2(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = [1 2]\nb = extend(a "a")').value).parse().node, context).error
            if e: raise e

    def test_keys_wrongtype(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = [1 2]\nb = keys(a)').value).parse().node, context).error
            if e: raise e

    def test_values_wrongtype(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = [1 2]\nb = values(a)').value).parse().node, context).error
            if e: raise e

    def test_open_wrongtype1(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = open(1 "r")').value).parse().node, context).error
            if e: raise e

    def test_open_wrongtype2(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = open("a" 1)').value).parse().node, context).error
            if e: raise e

    def test_open_nonexistent(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = open("nofile" "r")').value).parse().node, context).error
            if e: raise e

    def test_read_wrongtype(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('a = read(1)').value).parse().node, context).error
            if e: raise e

    def test_read_fileinwritemode(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('f = open("testfile" "w")\na = read("testfile")').value
                                 ).parse().node, context).error
            f = context.symbol_table.symbols['f'].fobj
            f.close()
            if e: raise e

    def test_write_wrongtype(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('write(1 "a")').value).parse().node, context).error
            if e: raise e

    def test_write_int(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('f = open("testfile" "w")\nwrite("testfile" 1)').value
                                 ).parse().node, context).error
            f = context.symbol_table.symbols['f'].fobj
            f.close()
            if e: raise e

    def test_write_fileinreadmode(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('f = open("testfile" "r")\nwrite("testfile" "a")').value
                                 ).parse().node, context).error
            f = context.symbol_table.symbols['f'].fobj
            f.close()
            if e: raise e

    def test_close_wrongtype(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('close(1)').value).parse().node, context).error
            if e: raise e

    def test_range_wrongtype(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('range("a")').value).parse().node, context).error
            if e: raise e

    def test_len_wrongtype(self):
        with self.assertRaises(RuntimeError):
            context.symbol_table = get_sym_table()
            e = RUN.visit(Parser(Lexer().tokenize('len(1)').value).parse().node, context).error
            if e: raise e


class TestInterpreterBasicWhile(unittest.TestCase):

    def test_sl_while(self):
        text = 'a=1\nwhile a < 10: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(10))

    def test_ml_while(self):
        text = 'a=1\nwhile a < 10{\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(10))

    def test_while_with_break(self):
        text = 'a=1\nwhile a < 5{\na += 1\nbreak\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(2))

    def test_while_without_continue(self):
        text = 'a=1\nwhile a < 5{\na += 1\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(5))

    def test_while_with_continue(self):
        text = 'a=1\nwhile a < 5{\na += 1\ncontinue\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(5))


class TestInterpreterBasicFor(unittest.TestCase):

    def test_sl_for_nostep(self):
        text = 'a=1\nfor i = 0 .. 7: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(8))

    def test_ml_for_nostep(self):
        text = 'a=1\nfor i = 0 .. 7{\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(8))

    def test_sl_for_withstep(self):
        text = 'a=1\nfor i = 0 .. 7 .. 2: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(5))

    def test_ml_for_withstep(self):
        text = 'a=1\nfor i = 0 .. 7 .. 2{\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(5))

    def test_sl_reverse_for_nostep(self):
        text = 'a=1\nfor i = 7 .. 0: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(8))

    def test_sl_reverse_for_withstep(self):
        text = 'a=1\nfor i = 7 .. 0 .. -1: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(8))

    def test_ml_reverse_for_nostep(self):
        text = 'a=1\nfor i = 7 .. 0{\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(8))

    def test_ml_reverse_for_withstep(self):
        text = 'a=1\nfor i = 7 .. 0 .. -1{\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(8))

    def test_for_with_break(self):
        text = 'a=1\nfor i = 1 .. 5{\na += 1\nbreak\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(2))

    def test_for_without_continue(self):
        text = 'a=1\nfor i = 1 .. 5{\na += 1\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(9))

    def test_for_with_continue(self):
        text = 'a=1\nfor i = 1 .. 5{\na += 1\ncontinue\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(5))

class TestInterpreterBasicForEach(unittest.TestCase):

    def test_sl_foreach(self):
        text = 'a=1\nforeach i in [0 1 2 3 4 5 6]: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(8))

    def test_ml_foreach(self):
        text = 'a=1\nforeach i in [0 1 2 3 4 5 6]{\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(8))

    def test_foreach_with_break(self):
        text = 'a=1\nforeach i in [0 1 2 3 4]{\na += 1\nbreak\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(2))

    def test_foreach_without_continue(self):
        text = 'a=1\nforeach i in [1 2 3 4]{\na += 1\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(9))

    def test_foreach_with_continue(self):
        text = 'a=1\nforeach i in [1 2 3 4]{\na += 1\ncontinue\na += 1\n}'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(5))


class TestInterpreterBasicIf(unittest.TestCase):

    # all combinations of conditionals in a single line
    def test_sl_if_true(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('? 1==1: 1').value
                                                 ).parse().node, context).value, Number(1))

    def test_sl_if_false(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=1\n? a>1: 5').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(1))

    def test_sl_if_elif_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('a=1\n? a==1: 5 !? a == 2: 6').value
                                                 ).parse().node, context).value.elements[-1], Number(5))

    def test_sl_if_elif_eliftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('a=1\n? a!=1: 5 !? a == 1: 6').value
                                                 ).parse().node, context).value.elements[-1], Number(6))

    def test_sl_if_elif_nonetrue(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=3\n? a==1: 5 !? a == 2: 6').value).parse().node, context)
        return self.assertEqual(context.symbol_table.get('a'), Number(3))

    def test_sl_if_else_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('a=1\n? a==1: 5 !: 6').value
                                                 ).parse().node, context).value.elements[-1], Number(5))

    def test_sl_if_else_iffalse(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('a=1\n? a!=1: 5 !: 6').value
                                                 ).parse().node, context).value.elements[-1], Number(6))

    def test_sl_if_elif_else_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('a=1\n? a==1: 4 !? a == 2: 5 !: 6').value
                                                 ).parse().node, context).value.elements[-1], Number(4))

    def test_sl_if_elif_else_eliftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('a=2\n? a==1: 4 !? a == 2: 5 !: 6').value
                                                 ).parse().node, context).value.elements[-1], Number(5))

    def test_sl_if_elif_else_elsetrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('a=3\n? a==1: 4 !? a == 2: 5 !: 6').value
                                                 ).parse().node, context).value.elements[-1], Number(6))

    # combinations of single- and multiline conditionals
    def test_ml_if_true(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('? 1==1{\n1\n}').value
                                                 ).parse().node, context).value, Number(1))

    def test_ml_if_false(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=1\n? a>1{\n5\n}').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(1))

    def test_ml_if_sl_elif_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('? 1==1{\n1\n}\n!? 1!=1: 2').value
                                                 ).parse().node, context).value, Number(1))

    def test_ml_if_sl_elif_iffalse(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1{\n1\n}\n!? 1==1: 2').value
                             ).parse().node, context).value, Number(2))

    def test_ml_if_sl_elif_bothfalse(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=1\n? a>1{\n5\n}\n!? a == 2: 7').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(1))

    def test_sl_if_ml_elif_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(RUN.visit(Parser(Lexer().tokenize('? 1==1:1\n!? 1!=1{\n2\n}').value
                                                 ).parse().node, context).value, Number(1))

    def test_sl_if_ml_elif_iffalse(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1:1\n!? 1==1{\n2\n}').value
                             ).parse().node, context).value, Number(2))

    def test_sl_if_ml_elif_bothfalse(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=1\n? a==2:5\n!? a!=1{\n7\n}').value).parse().node,
                  context)
        return self.assertEqual(context.symbol_table.get('a'), Number(1))

    def test_sl_if_sl_elif_ml_else_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1==1:1\n!? 2!=2: 2\n!{\n3\n}').value
                             ).parse().node, context).value, Number(1))

    def test_sl_if_sl_elif_ml_else_eliftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1:1\n!? 2==2: 2\n!{\n3\n}').value
                             ).parse().node, context).value, Number(2))

    def test_sl_if_sl_elif_ml_else_elsetrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1:1\n!? 2!=2: 2\n!{\n3\n}')
                             .value).parse().node, context).value, Number(3))

    def test_sl_if_ml_elif_sl_else_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1==1:1\n!? 2!=2{\n2\n}\n!: 3').value
                             ).parse().node, context).value, Number(1))

    def test_sl_if_ml_elif_sl_else_eliftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1:1\n!? 2==2{\n2\n}\n!: 3').value
                             ).parse().node, context).value, Number(2))

    def test_sl_if_ml_elif_sl_else_elsetrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1:1\n!? 2!=2{\n2\n}\n!: 3').value
                             ).parse().node, context).value, Number(3))

    def test_ml_if_sl_elif_sl_else_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1==1{\n1\n}\n!? 2!=2: 2\n!: 3').value
                             ).parse().node, context).value, Number(1))

    def test_ml_if_sl_elif_sl_else_eliftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1{\n1\n}\n!? 2==2: 2\n!: 3').value
                             ).parse().node, context).value, Number(2))

    def test_ml_if_sl_elif_sl_else_elsetrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1{\n1\n}\n!? 2!=2: 2\n!: 3').value
                             ).parse().node, context).value, Number(3))

    def test_sl_if_ml_elif_ml_else_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1==1:1\n!? 2!=2{\n2\n}\n!{\n3\n}').value
                             ).parse().node, context).value, Number(1))

    def test_sl_if_ml_elif_ml_else_eliftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1:1\n!? 2==2{\n2\n}\n!{\n3\n}').value
                             ).parse().node, context).value, Number(2))

    def test_sl_if_ml_elif_ml_else_elsetrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1:1\n!? 2!=2{\n2\n}\n!{\n3\n}').value
                             ).parse().node, context).value, Number(3))

    def test_ml_if_sl_elif_ml_else_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1==1{\n1\n}\n!? 2!=2: 2\n!{\n3\n}').value
                             ).parse().node, context).value, Number(1))

    def test_ml_if_sl_elif_ml_else_eliftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1{\n1\n}\n!? 2==2: 2\n!{\n3\n}').value
                             ).parse().node, context).value, Number(2))

    def test_ml_if_sl_elif_ml_else_elsetrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1{\n1\n}\n!? 2!=2: 2\n!{\n3\n}').value
                             ).parse().node, context).value, Number(3))

    def test_ml_if_ml_elif_ml_else_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1==1{\n1\n}\n!? 2!=2{\n2\n}\n!{\n3\n}').value
                             ).parse().node, context).value, Number(1))

    def test_ml_if_ml_elif_ml_else_eliftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1{\n1\n}\n!? 2==2{\n2\n}\n!{\n3\n}').value
                             ).parse().node, context).value, Number(2))

    def test_ml_if_ml_elif_ml_else_elsetrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1{\n1\n}\n!? 2!=2{\n2\n}\n!{\n3\n}').value
                             ).parse().node, context).value, Number(3))

    def test_sl_if_sl_elif_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1==1:1\n!? 1!=1: 2').value
                             ).parse().node, context).value, Number(1))

    def test_sl_if_sl_elif_iffalse(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1:1\n!? 1==1: 2').value
                             ).parse().node, context).value, Number(2))

    def test_sl_if_sl_elif_bothfalse(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a=1\n? a==2:5\n!? a!=1: 7').value
                         ).parse().node,context)
        return self.assertEqual(context.symbol_table.get('a'), Number(1))

    def test_sl_if_sl_elif_sl_else_iftrue(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1==1:1\n!? 1!=1: 2\n!: 3').value
                             ).parse().node, context).value, Number(1))

    def test_sl_if_sl_elif_sl_else_iffalse(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1!=1:1\n!? 1==1: 2\n!: 3').value
                             ).parse().node, context).value, Number(2))

    def test_sl_if_sl_elif_sl_else_bothfalse(self):
        context.symbol_table = get_sym_table()
        return self.assertEqual(
            RUN.visit(Parser(Lexer().tokenize('? 1==2:5\n!? 1!=1: 7\n!: 3').value
                             ).parse().node, context).value, Number(3))


class TestInterpreterBasicFunctions(unittest.TestCase):

    def test_anonymous_single_line_func_with_return(self):
        text = 'add = : [a b] <~ return a + b\na = add(4 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_anonymous_single_line_func_noreturn(self):
        text = 'add = : [a b] <~ a + b\na = add(4 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_named_single_line_func_with_return(self):
        text = ':add [a b] <~ return a + b\na = add(4 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_named_single_line_func_noreturn(self):
        text = ':add [a b] <~ a + b\na = add(4 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_anonymous_multiline_func_with_return(self):
        text = 'add = : [a b] <~{\nreturn a + b\n}\na = add(4 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_anonymous_multiline_func_noreturn(self):
        text = 'add = : [a b] <~{\na + b\n}\na = add(4 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(0))

    def test_named_multiline_func_with_return(self):
        text = ':add [a b] <~{\nreturn a + b\n}\na = add(4 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(6))

    def test_named_multiline_func_with_empty_return(self):
        text = ':add [a b] <~{\nc = a + b\nreturn\n}\na = add(4 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(0))

    def test_named_multiline_func_noreturn(self):
        text = ':add [a b] <~{\na + b\n}\na = add(4 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(0))

    def test_named_single_line_func_noargs_noreturn(self):
        text = ':add [] <~ 1 + 1\na = add()'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(2))

    def test_anonymous_single_line_func_noargs_noreturn(self):
        text = 'num = : [] <~ 1 + 1\na = num()'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['a'], Number(2))

    # need tests for no argument functions and wrong number of arguments


class TestInterpreterBasicWhen(unittest.TestCase):

    def test_sl_when_dynamic(self):
        text = 'a=1\nb=0\nwhen a == 10: b = 57\nwhile b != 57: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['a'] == Number(10)
        b = context.symbol_table.symbols['b'] == Number(57)
        self.assertTrue(a and b)

    def test_sl_when_once(self):
        text = 'a=1\nb=0\nwhen a == 10{\nb = 57\nonce\n}\nwhile b != 57: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['a'].triggers
        self.assertEqual(a, [])

    def test_intentionally_trigger_when_with_equals_dynamic(self):
        text = 'a=1\nb=0\nwhen a == 10: b = 57\na = 10'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['b'], Number(57))

    def test_intentionally_trigger_when_with_acc_dynamic(self):
        text = 'a=8\nb=0\nwhen a == 10: b = 57\na += 2'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['b'], Number(57))

    def test_ml_when_dynamic(self):
        text = 'a=1\nb=0\nwhen a == 10{\nb = 57\n}\nwhile b != 57: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['a'] == Number(10)
        b = context.symbol_table.symbols['b'] == Number(57)
        self.assertTrue(a and b)

    def test_sl_when_static(self):
        text = 'a=1\nb=0\nwhen a == 10: b = 57\nwhile b != 57: a += 1'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['a'] == Number(10)
        b = context.symbol_table.symbols['b'] == Number(57)
        self.assertTrue(a and b)

    def test_intentionally_trigger_when_with_equals_static(self):
        text = 'a=1\nb=0\nwhen a == 10: b = 57\na = 10'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['b'], Number(57))

    def test_intentionally_trigger_when_with_equals_static_2(self):
        text = 'a=1.0\nb=0\nwhen a == 10: b = 57\na = 10'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['b'], Number(57))

    def test_intentionally_trigger_when_with_acc_static(self):
        text = 'a=8\nb=0\nwhen a == 10: b = 57\na += 2'
        context.symbol_table = get_sym_table()
        context.symbol_table.set('static-typing', Number(1))
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.symbols['b'], Number(57))

    def test_ml_when_static(self):
        text = 'use static\na=1\nb=0\nwhen a == 10{\nb = 57\n}\nwhile b != 57: a += 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['a'] == Number(10)
        b = context.symbol_table.symbols['b'] == Number(57)
        self.assertTrue(a and b)


class TestInterpreterBasicStruct(unittest.TestCase):

    def test_basic_struct(self):
        text = '::mytype [a] {\nx = a\n}\nmyvar = mytype(1)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['myvar']
        self.assertEqual(a.properties, {'x': Number(1)})

    def test_basic_struct_noargs(self):
        text = '::mytype [] {\nx = 1\n}\nmyvar = mytype()'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['myvar']
        self.assertEqual(a.properties, {'x': Number(1)})

    def test_basic_unnamed_struct(self):
        text = 'mytype = :: [a] {\nx = a\n}\nmyvar = mytype(1)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['myvar']
        self.assertEqual(a.properties, {'x': Number(1)})

    def test_basic_unnamed_struct_noargs(self):
        text = 'mytype = :: [] {\nx = 1\n}\nmyvar = mytype()'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['myvar']
        self.assertEqual(a.properties, {'x': Number(1)})

    def test_basic_struct_property_access(self):
        text = '::mytype [a] {\nx = a\n}\nmyvar = mytype(1)\na=myvar.x'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        self.assertEqual(context.symbol_table.get('a'), Number(1))

    def test_basic_struct_modify_property(self):
        text = '::mytype [a] {\nx = a\n}\nmyvar = mytype(1)\nmyvar.x=12'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['myvar']
        self.assertEqual(a.properties, {'x': Number(12)})

    def test_basic_struct_interface(self):
        text = '::mytype [a] {\nx = a\n.add <~ x\n}\n:add [a b] <~ a + b\nmyvar = mytype(17)\nval = add(myvar 3)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        val = context.symbol_table.symbols['val']
        self.assertEqual(val, Number(20))

    def test_basic_struct_in_func_nointerface(self):
        text = '::mytype [a] {\nx = a\n}\n:getx [a]<~ a.x \nmyvar = mytype(17)\nval = getx(myvar)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        val = context.symbol_table.symbols['val']
        self.assertEqual(val, Number(17))

    def test_basic_dot(self):
        text = '::mytype [a] {\nx = a\n}\nmyvar = mytype(1)\nmyval = myvar.x'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['myval']
        self.assertEqual(a, Number(1))


class TestInterpreterBasicImports(unittest.TestCase):

    def test_basic_moduleimport(self):
        text = 'use testfiles\\moduletest\na = add(1 2)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['a']
        self.assertEqual(a, Number(3))

    # need to clean this up; it doesn't pass if there isn't a line after use
    def test_basic_usestatic(self):
        text = 'use static\na = 1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['static-typing']
        self.assertEqual(a, Number(1))


class TestInterpreterBuiltinFunctions(unittest.TestCase):

    def test_print(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('print(1)').value).parse().node,
                  context)
        return self.assertEqual(a.value, Number(0))

    def test_rprint(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('rprint(5)').value).parse().node,
                      context)
        return self.assertEqual(a.value, String("5"))

    def test_isnum_true(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('isnum(5)').value).parse().node,
                      context)
        return self.assertEqual(a.value, Number(1))

    def test_isnum_false(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('isnum("abc")').value).parse().node,
                      context)
        return self.assertEqual(a.value, Number(0))

    def test_isstr_true(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('isstr("abc")').value).parse().node,
                      context)
        return self.assertEqual(a.value, Number(1))

    def test_isstr_false(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('isstr(5)').value).parse().node,
                      context)
        return self.assertEqual(a.value, Number(0))

    def test_islst_true(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('islst([1 2])').value).parse().node,
                      context)
        return self.assertEqual(a.value, Number(1))

    def test_islst_false(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('islst(5)').value).parse().node,
                      context)
        return self.assertEqual(a.value, Number(0))

    def test_isfun_true(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('a = : [x y] <~ x+y\nisfun(a)').value).parse().node,
                      context)
        return self.assertEqual(a.value.elements[-1], Number(1))

    def test_isfun_false(self):
        context.symbol_table = get_sym_table()
        a = RUN.visit(Parser(Lexer().tokenize('isfun(5)').value).parse().node,
                      context)
        return self.assertEqual(a.value, Number(0))

    def test_append(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a = [1 2]\nappend(a 5)').value).parse().node,
                  context)
        res = context.symbol_table.get('a').elements
        return self.assertEqual(res, [Number(1), Number(2), Number(5)])

    def test_extend(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a = [1 2]\nextend(a [5 6])').value).parse().node,
                  context)
        res = context.symbol_table.get('a').elements
        return self.assertEqual(res, [Number(1), Number(2),
                                      Number(5), Number(6)])

    def test_pop_element(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a = [1 2 3]\nb = pop(a 1)').value).parse().node,
                  context)
        res = context.symbol_table.get('b')
        return self.assertEqual(res, Number(2))

    def test_pop_list(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('a = [1 2 3]\nb = pop(a 1)').value).parse().node,
                  context)
        res = context.symbol_table.get('a')
        return self.assertEqual(res, List([Number(1), Number(3)]))

    def test_pop_listproperty(self):
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('::u [x] {\ny = x\n}\na = u([1 2 3])\nb = pop(a.y 1)').value).parse().node,
                  context)
        res = context.symbol_table.symbols['a'].properties['y']
        return self.assertEqual(res, List([Number(1), Number(3)]))

    def test_range(self):
        context.symbol_table = get_sym_table()
        res = RUN.visit(Parser(Lexer().tokenize('range(3)').value).parse().node, context).value
        return self.assertEqual(res, List([Number(0), Number(1), Number(2)]))

    def test_len_list(self):
        context.symbol_table = get_sym_table()
        res = RUN.visit(Parser(Lexer().tokenize('len([1 2])').value).parse().node, context).value
        return self.assertEqual(res, Number(2))

    def test_len_emptylist(self):
        context.symbol_table = get_sym_table()
        res = RUN.visit(Parser(Lexer().tokenize('len([])').value).parse().node, context).value
        return self.assertEqual(res, Number(0))

    def test_len_str(self):
        context.symbol_table = get_sym_table()
        res = RUN.visit(Parser(Lexer().tokenize('len("ab")').value).parse().node, context).value
        return self.assertEqual(res, Number(2))

    def test_len_emptystr(self):
        context.symbol_table = get_sym_table()
        res = RUN.visit(Parser(Lexer().tokenize('len("")').value).parse().node, context).value
        return self.assertEqual(res, Number(0))

    def test_len_map(self):
        context.symbol_table = get_sym_table()
        res = RUN.visit(Parser(Lexer().tokenize('len({1:2 2:3})').value).parse().node, context).value
        return self.assertEqual(res, Number(2))

    def test_len_emptymap(self):
        context.symbol_table = get_sym_table()
        res = RUN.visit(Parser(Lexer().tokenize('len({})').value).parse().node, context).value
        return self.assertEqual(res, Number(0))

    def test_keys(self):
        context.symbol_table = get_sym_table()
        res = RUN.visit(Parser(Lexer().tokenize('keys({"a":1 2:"b"})').value).parse(
            ).node, context).value
        return self.assertEqual(res, List([String("a"), Number(2)]))

    def test_values(self):
        context.symbol_table = get_sym_table()
        res = RUN.visit(Parser(Lexer().tokenize('values({"a":1 2:"b"})').value).parse(
        ).node, context).value
        return self.assertEqual(res, List([Number(1), String("b")]))

    def test_fileopen(self):
        if os.path.exists('mytest'):
            os.remove('mytest')
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize('f = open("mytest" "w")\nclose(f)').value
                         ).parse().node, context)
        return self.assertTrue(os.path.exists('mytest'))

    def test_filewrite(self):
        if os.path.exists('mytest'): os.remove('mytest')
        text = 'f = open("mytest" "w")\nwrite(f "Hello World")\nclose(f)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value
                         ).parse().node, context)
        data = ''
        if os.path.exists('mytest'):
            f = open('mytest', 'r')
            data = f.read()
            f.close()
        return self.assertTrue(data, '"Hello World"')

    def test_fileread(self):
        if os.path.exists('mytest'): os.remove('mytest')
        text = 'f = open("mytest" "w")\nwrite(f "ReAd TeSt")\nclose(f)\n'
        text += 'f = open("mytest" "r")\ndata = read(f)\nclose(f)'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        data = context.symbol_table.symbols['data']
        return self.assertTrue(data, '"ReAd TeSt"')


class TestInterpreterChainedAccessOperators(unittest.TestCase):

    def test_atlist_then_atlist_access(self):
        text = '[[9 8] [7 6]] @ 0 @ 1'
        context.symbol_table = get_sym_table()
        result = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).value
        return self.assertEqual(result, Number(8))

    def test_dot_then_dot_access(self):
        text = '::u [a] {\nx = a\n}\n::v [b] {\ny = b\n}\nm = u(11)\nn = v(m)\nmyvar = n.y.x'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['myvar']
        return self.assertEqual(a, Number(11))

    def test_atlist_then_atlist_assignment(self):
        text = 'a = [[9 8] [7 6]]\na@0@1 = 54'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['a'].elements[0].elements[1]
        return self.assertEqual(a, Number(54))

    def test_dot_then_dot_assignment(self):
        text = '::u [a] {\nx = a\n}\n::v [b] {\ny = b\n}\nm = u(11)\nn = v(m)\nn.y.x = 99'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['n'].properties['y'].properties['x']
        return self.assertEqual(a, Number(99))

    def test_dot_then_dot_plsassignment(self):
        text = '::u [a] {\nx = a\n}\n::v [b] {\ny = b\n}\nm = u(11)\nn = v(m)\nn.y.x += 99'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['n'].properties['y'].properties['x']
        return self.assertEqual(a, Number(110))

    def test_dot_then_dot_mnsassignment(self):
        text = '::u [a] {\nx = a\n}\n::v [b] {\ny = b\n}\nm = u(11)\nn = v(m)\nn.y.x -= 99'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['n'].properties['y'].properties['x']
        return self.assertEqual(a, Number(-88))

    def test_dot_then_dot_mulassignment(self):
        text = '::u [a] {\nx = a\n}\n::v [b] {\ny = b\n}\nm = u(1)\nn = v(m)\nn.y.x *= 99'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['n'].properties['y'].properties['x']
        return self.assertEqual(a, Number(99))

    def test_dot_then_dot_divassignment(self):
        text = '::u [a] {\nx = a\n}\n::v [b] {\ny = b\n}\nm = u(20)\nn = v(m)\nn.y.x /= 4'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['n'].properties['y'].properties['x']
        return self.assertEqual(a, Number(5))

    def test_dot_then_dot_powassignment(self):
        text = '::u [a] {\nx = a\n}\n::v [b] {\ny = b\n}\nm = u(2)\nn = v(m)\nn.y.x ^= 3'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['n'].properties['y'].properties['x']
        return self.assertEqual(a, Number(8))

    def test_dot_then_dot_modassignment(self):
        text = '::u [a] {\nx = a\n}\n::v [b] {\ny = b\n}\nm = u(11)\nn = v(m)\nn.y.x %= 6'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        a = context.symbol_table.symbols['n'].properties['y'].properties['x']
        return self.assertEqual(a, Number(5))

    def test_atlist_then_dot_access(self):
        text = '::u [a] {\nx = a\n}\nm = u(11)\nn = [1 2 m]\nq = (n @ 2).x'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        q = context.symbol_table.symbols['q']
        return self.assertEqual(q, Number(11))

    def test_dot_then_atlist_access(self):
        text = '::u [a] {\nx = a\n}\nm = u([5 7 9])\nq = m.x@2'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        q = context.symbol_table.symbols['q']
        return self.assertEqual(q, Number(9))

    def test_atlist_then_dot_assignment(self):
        text = '::u [a] {\nx = a\n}\nm = u(11)\nn = [1 2 m]\n(n @ 2).x = 76'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        q = context.symbol_table.symbols['n'].elements[2].properties['x']
        return self.assertEqual(q, Number(76))

    def test_dot_then_atlist_assignment(self):
        text = '::u [a] {\nx = a\n}\nm = u([5 7 9])\nm.x@2 = 44'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        q = context.symbol_table.symbols['m'].properties['x'].elements[2]
        return self.assertEqual(q, Number(44))

    def test_atmap_then_atmap_access(self):
        text = '{1: {3: "a" 4: "b"} 2: {5: "c" 6: "d"}} @ 1 @ 3'
        context.symbol_table = get_sym_table()
        result = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).value
        return self.assertEqual(result, String("a"))

    def test_atmap_then_atmap_assignment(self):
        text = 'a = {1: {3: "a" 4: "b"} 2: {5: "c" 6: "d"}}\na @ 1 @ 3 = "success"'
        context.symbol_table = get_sym_table()
        result = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).value
        q = context.symbol_table.symbols['a'].elements[Number(1)].elements[Number(3)]
        return self.assertEqual(q, String("success"))

    def test_atmap_then_dot_access(self):
        text = '::u [a] {\nx = a\n}\nm = u(5)\nmymap = {1: m 2: 3}\nq = (mymap@1).x'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        q = context.symbol_table.symbols['q']
        return self.assertEqual(q, Number(5))

    def test_dot_then_atmap_access(self):
        text = '::u [a] {\nx = a\n}\nmymap = {1: "abc" 2: 3}\nm = u(mymap)\nq = m.x@1'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        q = context.symbol_table.symbols['q']
        return self.assertEqual(q, String("abc"))

    def test_atmap_then_dot_assignment(self):
        text = '::u [a] {\nx = a\n}\nm = u(5)\nmymap = {1: m 2: 3}\n(mymap@1).x = 10'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        q = context.symbol_table.symbols['mymap'].elements[Number(1)].properties['x']
        return self.assertEqual(q, Number(10))

    def test_dot_then_atmap_assignment(self):
        text = '::u [a] {\nx = a\n}\nmymap = {1: "abc" 2: 3}\nm = u(mymap)\nm.x@1 = "def"'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        q = context.symbol_table.symbols['m'].properties['x'].elements[Number(1)]
        return self.assertEqual(q, String("def"))

    def test_dot_then_atstr_access(self):
        text = '::u [a] {\nx = a\n}\nm = u("abcde")\nq = m.x@2'
        context.symbol_table = get_sym_table()
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context)
        q = context.symbol_table.symbols['q']
        return self.assertEqual(q, String('c'))

    def test_atlist_then_atmap_access(self):
        text = '[{"a": 1 "b": 2} [7 6]] @ 0 @ "a"'
        context.symbol_table = get_sym_table()
        result = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).value
        return self.assertEqual(result, Number(1))

    def test_atlist_then_atstr_access(self):
        text = '["abcde" [7 6]] @ 0 @ 1'
        context.symbol_table = get_sym_table()
        result = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).value
        return self.assertEqual(result, String('b'))

    def test_atmap_then_atlist_access(self):
        text = '{"a": [1 14] "b": 2} @ "a" @ 1'
        context.symbol_table = get_sym_table()
        result = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).value
        return self.assertEqual(result, Number(14))

    def test_atmap_then_atstr_access(self):
        text = '{"a": "cdefg" "b": 2} @ "a" @ 1'
        context.symbol_table = get_sym_table()
        result = RUN.visit(Parser(Lexer().tokenize(text).value).parse().node, context).value
        return self.assertEqual(result, String('d'))


class TestInterpreterErrorHandler(unittest.TestCase):

    def test_basic_sl_try_sl_catch_trysucceeds(self):
        context.symbol_table = get_sym_table()
        text = 'a=1\ntry:a=a/1\ncatch:a=a*3'
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node,
                  context)
        res = context.symbol_table.get('a')
        return self.assertEqual(res, Number(1))

    def test_basic_sl_try_sl_catch_tryfails(self):
        context.symbol_table = get_sym_table()
        text = 'a=1\ntry:a=a/0\ncatch:a=a*3'
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node,
                  context)
        res = context.symbol_table.get('a')
        return self.assertEqual(res, Number(3))

    def test_basic_ml_try_sl_catch_trysucceeds(self):
        context.symbol_table = get_sym_table()
        text = 'a=1\nb=2\ntry{\nb=10\na=a/1\n}\ncatch:a=a*3'
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node,
                  context)
        res = context.symbol_table.get('a')
        return self.assertEqual(res, Number(1))

    def test_basic_ml_try_sl_catch_tryfails(self):
        context.symbol_table = get_sym_table()
        text = 'a=1\nb=2\ntry{\nb=10\na=a/0\n}\ncatch:a=a*3'
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node,
                  context)
        res = context.symbol_table.get('a')
        return self.assertEqual(res, Number(3))

    def test_basic_sl_try_ml_catch_trysucceeds(self):
        context.symbol_table = get_sym_table()
        text = 'a=1\ntry:a=a/1\ncatch{\nb=10\na=a*3}'
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node,
                  context)
        res = context.symbol_table.get('a')
        return self.assertEqual(res, Number(1))

    def test_basic_sl_try_ml_catch_tryfails(self):
        context.symbol_table = get_sym_table()
        text = 'a=1\ntry:a=a/0\ncatch{\nb=10\na=a*3}'
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node,
                  context)
        res = context.symbol_table.get('a')
        return self.assertEqual(res, Number(3))

    def test_basic_ml_try_ml_catch_trysucceeds(self):
        context.symbol_table = get_sym_table()
        text = 'a=1\ntry{\nb=10\na=a/1\n}\ncatch{\nb=10\na=a*3}'
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node,
                  context)
        res = context.symbol_table.get('a')
        return self.assertEqual(res, Number(1))

    def test_basic_ml_try_ml_catch_tryfails(self):
        context.symbol_table = get_sym_table()
        text = 'a=1\ntry{\nb=10\na=a/0\n}\ncatch{\nb=10\na=a*3}'
        RUN.visit(Parser(Lexer().tokenize(text).value).parse().node,
                  context)
        res = context.symbol_table.get('a')
        return self.assertEqual(res, Number(3))

# END INTERPRETER SECTION


def main():
    unittest.main()

if __name__ == '__main__':
    main()
