from .errors import *
from .node import *
from .result import ParseResult
from .typedef import Token
from . import constants as c


class Parser:
    """
    """
    def __init__(self, tokens, symbol_table=None):
        self.warnings = []
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.static = False
        if symbol_table:
            if self.symbol_table.get('static-typing').is_true():
                self.static = True
        self.tok_idx = -1
        self.previous_tok = self.current_tok = None
        self.advance()

    def update(self, res):
        res.register_advancement()
        self.advance()

    # move to next token
    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    # go back if a read operation failed
    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    # get current token
    def update_current_tok(self):
        if 0 <= self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        if 0 < self.tok_idx < len(self.tokens):
            self.previous_tok = self.tokens[self.tok_idx - 1]
        else: self.previous_tok = None

    # look at token amt spaces ahead of the current one
    def peek(self, amt=1):
        if self.tok_idx < len(self.tokens) - amt:
            return self.tokens[self.tok_idx + amt]

    # entry point for parsing
    def parse(self):
        res = self.statements()
        # check if there is still an error hanging out from inside the code
        # this makes sure any scopes still open at EOF throw an error
        if res.resid_err:
            return res.failure(res.resid_err)
        if res.error:
            return res
        return res

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        self.consume_newlines(res)

        # read in first statement
        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True
        e = None

        # read in any additional statements
        # TODO: REFACTOR THIS THIS IS AWFUL
        while True:
            newline_count = 0
            while self.current_tok.type == 'BREAK':
                self.update(res)
                newline_count += 1
            if isinstance(statements[-1], UseNode):
                newline_count += 1
            if isinstance(statements[-1], IfNode):
                newline_count += 1
            if newline_count == 0:
                more_statements = False
            if self.current_tok.type == 'EOF':
                more_statements = False
                # if e: return res.failure(e)

            if not more_statements: break
            statement, e = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                res.resid_err = e
                continue
            else:
                res.resid_err = None
            statements.append(statement)

        retidx = -1
        n = len(statements)
        for i in range(n):
            if isinstance(statements[i], ReturnNode):
                retidx = i
                break
        if -1 < retidx < n - 1:
            return res.failure(InvalidSyntaxError(statements[-1].pos_start,
                                                  statements[-1].pos_end,
                                                  "Return statement must come last"))

        return res.success(CapsuleNode(statements,
                                       pos_start,
                                       self.current_tok.pos_end.copy()))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        # use keyword handler
        if self.accept_keyword(res, 'use'):
            # use must be followed by an identifier
            self.expect_token_type(res, c.ID_SYM)
            if res.error: return res
            fname = self.previous_tok

            # use must be followed by newline
            if self.accept_newline(res) or self.current_tok.matches(Token('EOF', None)): pass
            else: return res.failure(InvalidSyntaxError(pos_start,
                                                        self.current_tok.pos_end,
                                                        f'Expected newline'))
            return res.success(UseNode(fname))

        # return keyword handler
        if self.accept_keyword(res, 'return'):
            expr, _ = res.try_register(self.expr())
            if not expr: self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr,
                                          pos_start,
                                          self.current_tok.pos_start.copy()))

        # del keyword handler
        if self.accept_keyword(res, 'del'):
            self.expect_token_type(res, c.ID_SYM)
            if res.error: return res

            to_delete = self.previous_tok
            return res.success(DeleteNode(to_delete))

        # continue keyword handler
        if self.accept_keyword(res, 'continue'):
            return res.success(ContinueNode(pos_start,
                                            self.current_tok.pos_start.copy()))

        # once keyword handler
        if self.accept_keyword(res, 'once'):
            return res.success(OnceNode(pos_start,
                                        self.current_tok.pos_start.copy()))

        # break keyword handler
        if self.accept_keyword(res, 'break'):
            return res.success(BreakNode(pos_start,
                                         self.current_tok.pos_start.copy()))

        # try to read expression if no keyword statements found
        expr = res.register(self.expr())
        if res.error: return res

        return res.success(expr)

    def expr(self):
        res = ParseResult()
        warn_msg = ''

        statictype = 'default'

        # check for constant declaration
        constvar = self.accept_optional(res, c.ID_KWD, 'const')

        # check for global declaration
        globalvar = self.accept_optional(res, c.ID_KWD, 'global')

        # warning about unnecessary var keyword
        if self.accept_optional(res, c.ID_KWD, 'var'):
            if not self.static:
                warn_msg = f'kwd <var> has no effect'
            statictype = 'var'

        # check for explicit type definition
        # if self.current_tok.value in ['int', 'flt', 'str', 'lst', 'map']:
        if self.accept_one_optional(res, ['int', 'flt', 'str', 'lst', 'map']):
            statictype = self.previous_tok.value

        # try to read a function definition
        if self.accept_operator(res, ':'):
            f = res.register(self.func_def())
            if res.error: return res
            return res.success(f)

        # try to read a struct definition
        if self.accept_operator(res, '::'):
            s = res.register(self.struct_def())
            if res.error: return res
            return res.success(s)

        # try to read an interface definition
        if self.accept(res, 'DOT', '.'):
            i = res.register(self.interface_def())
            if res.error: return res
            return res.success(i)

        # regular named variable assignment
        if self.current_tok.type == c.ID_SYM and self.peek().type == c.ID_ASG:
            var_name = self.current_tok
            self.update(res)

            op_tok = self.current_tok
            self.update(res)

            expr = res.register(self.expr())
            if res.error: return res
            if warn_msg: self.warnings.append(warn_msg)

            return res.success(VarAssignNode(var_name,
                                            op_tok,
                                            expr,
                                            constvar=constvar,
                                            globalvar=globalvar,
                                            statictype=statictype))

        # try to read a comparison expression
        node = res.register(self.bin_op(self.comp_expr, ('AND',
                                                         'INJ',
                                                         'IN',
                                                         'NAND',
                                                         'NOR',
                                                         'OR',
                                                         'XOR')))
        if res.error: return res
        if warn_msg: self.warnings.append(warn_msg)

        # if successful, check if the expression was on the left side of an
        # assignment or augassignment operator
        if self.current_tok.type == c.ID_ASG:

            op_tok = self.current_tok
            self.update(res)

            expr = res.register(self.expr())
            if res.error: return res
            if warn_msg: self.warnings.append(warn_msg)

            # if we find an expression on the right hand side, create a node to
            # assign a value to the chained access expression
            node = ReferenceAccessNode(ReferenceAssignNode(node,
                                                           op_tok,
                                                           expr))
            return res.success(node)

        return res.success(node)

    def comp_expr(self):
        res = ParseResult()

        # check for not expression
        if self.accept_token_type(res, 'NOT'):
            op_tok = self.previous_tok
            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))

        # if not is not present, try to read a comparator expression
        node = res.register(self.bin_op(self.arith_expr, ('EQ', 'NE', 'LT', 'GT', 'LE', 'GE')))
        if res.error: return res
        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, ('PLS', 'MNS'))

    def term(self):
        return self.bin_op(self.factor, ('MUL', 'DIV', 'MOD'))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        # check for negative numbers
        if self.accept_one_token_type(res, ['PLS', 'MNS']):
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.index, ('POW',), self.factor)

    def index(self):
        return self.bin_op(self.property, ('LSLC', 'RSLC', 'AT'), self.property)

    def property(self):
        # right now, dot operators take precedence over slices and indexes
        # this is because a dot can only be followed by an identifier
        return self.bin_op(self.call, ('DOT',), self.atom)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == 'LPR':
            self.update(res)
            arg_nodes = []

            if self.current_tok.type == 'RPR':
                self.update(res)
            else:
                while self.current_tok.type != 'RPR':
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                    if self.current_tok.type == 'EOF':
                        return res.failure(PrematureEOFError(self.current_tok.pos_start,
                                                             self.current_tok.pos_end,
                                                             f"Expected ')'"))

                self.update(res)

            return res.success(CallNode(atom, arg_nodes))

        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        # kwds = {'LBR': 'list_expr',
        #         'LCR': 'map_expr',
        #         'for: ': 'for_expr',
        #         'foreach': 'foreach_expr',
        #         'while': 'while_expr',
        #         'when': 'when_expr',
        #         'defer': 'defer_expr',
        #         'try': 'try_expr'}

        # register number
        if self.accept_one_token_type(res, [c.ID_INT, c.ID_FLT]):
            return res.success(NumberNode(tok))

        # register string
        elif self.accept_one_token_type(res, [c.ID_STR, 'FSTR']):
            return res.success(StringNode(tok))

        # register identifier
        elif self.accept_token_type(res, c.ID_SYM):
            return res.success(VarAccessNode(tok))

        # register parenthetical expression
        elif self.accept_token_type(res, 'LPR'):
            expr = res.register(self.expr())
            if res.error: return res

            self.expect_token_type(res, 'RPR')
            # TODO: I just added this line and it didn't change the test suite.
            # Am I forgetting to try an unclosed parenthetical expression?
            if res.error: return res
            return res.success(expr)

        # register list
        elif self.accept_token_type(res, 'LBR'):
            return self.try_process_keyword(res, 'list_expr')

        # register map
        elif self.accept_token_type(res, 'LCR'):
            return self.try_process_keyword(res, 'map_expr')

        # register conditional chain
        elif tok.matches(Token(c.ID_KWD, '?')) or tok.matches(Token(c.ID_KWD, 'if')):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        # register for loop
        elif self.accept_keyword(res, 'for'):
            return self.try_process_keyword(res, 'for_expr')

        # register iterator loop
        elif self.accept_keyword(res, 'foreach'):
            return self.try_process_keyword(res, 'foreach_expr')

        # register while loop
        elif self.accept_keyword(res, 'while'):
            return self.try_process_keyword(res, 'while_expr')

        # register when trigger
        elif self.accept_keyword(res, 'when'):
            return self.try_process_keyword(res, 'when_expr')

        # register defer block
        elif self.accept_keyword(res, 'defer'):
            return self.try_process_keyword(res, 'defer_expr')

        # register try/catch block
        elif self.accept_keyword(res, 'try'):
            return self.try_process_keyword(res, 'try_expr')

        # register function definition
        elif self.accept_operator(res, ':'):
            return self.try_process_keyword(res, 'func_def')

        # register struct definition
        elif self.accept_operator(res, '::'):
            return self.try_process_keyword(res, 'struct_def')

        # else:
        #     for kwd, func in kwds.items():
        #         if self.accept_keyword(res, kwd):
        #             return self.try_process_keyword(res, func)

        return res.failure(InvalidSyntaxError(tok.pos_start,
                                              tok.pos_end,
                                              "Expected atom"))

    def try_process_keyword(self, res, func):
        func_pointer = getattr(self, func, Parser.process_function_not_defined)
        val = res.register(func_pointer())
        if res.error: return res
        return res.success(val)

    @staticmethod
    def process_function_not_defined(res, func):
        raise Exception(f'No process function defined for {func}.')

    def map_expr(self):
        res = ParseResult()
        elements = {}
        pos_start = self.current_tok.pos_start.copy()

        if not self.accept_token_type(res, 'RCR'):
            # format is { expr : expr expr : expr ... }
            # newlines help with clarity, e.g.
            # { expr : expr
            #   expr : expr ... }
            while self.current_tok.type not in ['RCR', 'EOF']:
                key = res.register(self.expr())
                if res.error:
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                          self.current_tok.pos_end,
                                                          "Expected expression or '}'"))

                self.expect_operator(res, ':')
                if res.error: return res

                value = res.register(self.expr())
                if res.error: return res

                elements[key] = value
                self.consume_newlines(res)

            self.expect(res, 'RCR', '}', message="Expected expression or '}'", err_type=UnclosedScopeError)
            if res.error: return res

        return res.success(MapNode(elements,
                                   pos_start,
                                   self.current_tok.pos_end.copy()))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if not self.accept_token_type(res, 'RBR'):
            # format is [ expr expr ... ]
            while self.current_tok.type not in ['RBR', 'EOF']:
                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                          self.current_tok.pos_end,
                                                          "Expected expression or ']'"))

            self.expect(res, 'RBR', ']', message="Expected ']'", err_type=UnclosedScopeError)
            if res.error: return res

        return res.success(ListNode(element_nodes,
                                    pos_start,
                                    self.current_tok.pos_end.copy()))

    # entry point for conditional chains
    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases(('?', 'if')))
        if res.error: return res

        cases, else_case = all_cases
        return res.success(IfNode(cases,
                                  else_case))

    def if_expr_b(self):
        return self.if_expr_cases(('!?', 'elif'))

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        # grab else block
        if self.current_tok.value in ('!', 'else'):
            self.update(res)

            if self.current_tok.type == 'LCR':
                self.update(res)

                self.expect_newline(res)
                if res.error: return res

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)
                if res.error: return res

            else:
                self.expect_operator(res, ':')
                # TODO: I added this line during editing. All tests were passing beforehand.
                # Does that mean I haven't tested some case?
                if res.error: return res

                expr = res.register(self.expr())
                if res.error: return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        self.consume_newlines(res)

        if self.current_tok.value in ('!?', 'elif'):
            all_cases = res.register(self.if_expr_b())
            if res.error: return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error: return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keywords):
        res = ParseResult()
        cases = []
        else_case = None

        self.expect_one(res, case_keywords)
        if res.error: return res

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type == 'LCR':
            self.update(res)

            self.expect_newline(res)
            if res.error: return res

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_tok.type == 'RCR':
                self.update(res)

                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res

                new_cases, else_case = all_cases
                cases.extend(new_cases)
            else: return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                        self.current_tok.pos_end,
                                                        "Expected '}'"))

        else:
            self.expect_operator(res, ':', err_type=UnopenedScopeError)
            if res.error: return res

            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def for_expr(self):
        res = ParseResult()

        self.expect_token_type(res, c.ID_SYM)
        if res.error: return res
        var_name = self.previous_tok

        self.expect(res, 'ASG', '=')
        if res.error: return res

        start_value = res.register(self.expr())
        if res.error: return res

        self.expect_operator(res, '..')
        if res.error: return res

        end_value = res.register(self.expr())
        if res.error: return res

        if self.accept_operator(res, '..'):
            step_value = res.register(self.expr())
            if res.error: return res
        else: step_value = None

        body, _ = self.parse_statement_or_block(res)
        if res.error:
            return res

        return res.success(ForNode(var_name,
                                   start_value,
                                   end_value,
                                   step_value,
                                   body,
                                   False))

    def foreach_expr(self):
        res = ParseResult()

        if self.current_tok.type != c.ID_SYM:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected identifier"))
        var_name = self.current_tok
        self.update(res)

        self.expect_keyword(res, 'in')
        if res.error: return res

        container = res.register(self.expr())
        if res.error: return res

        body, _ = self.parse_statement_or_block(res)
        if res.error:
            return res

        return res.success(ForEachNode(var_name,
                                       container,
                                       body,
                                       False))

    def while_expr(self):
        res = ParseResult()

        condition = res.register(self.expr())
        if res.error: return res

        body, _ = self.parse_statement_or_block(res)
        if res.error:
            return res

        return res.success(WhileNode(condition,
                                     body,
                                     False))

    def when_expr(self):
        res = ParseResult()

        condition = res.register(self.expr())
        if res.error: return res

        body, _ = self.parse_statement_or_block(res)
        if res.error:
            return res

        return res.success(WhenNode(condition,
                                    body,
                                    True))

    def defer_expr(self):
        res = ParseResult()

        body, _ = self.parse_statement_or_block(res)
        if res.error:
            return res

        return res.success(DeferNode(body,
                                     False))

    def try_expr(self):
        res = ParseResult()

        try_tok = self.previous_tok

        try_node, _ = self.parse_statement_or_block(res)
        if res.error:
            return res

        self.consume_newlines(res)

        self.expect_keyword(res, 'catch')
        if res.error: return res

        catch_node, _ = self.parse_statement_or_block(res)
        if res.error:
            return res

        return res.success(ErrorHandlerNode(try_tok, try_node, catch_node))

    def func_def(self):
        res = ParseResult()

        if self.accept_token_type(res, c.ID_SYM):
            var_name_tok = self.previous_tok
            self.expect_token_type(res, 'LBR', err_type=UnopenedScopeError)
            if res.error: return res

        else:
            var_name_tok = None
            self.expect_token_type(res, 'LBR', err_type=UnopenedScopeError)
            if res.error: return res

        arg_name_toks = []
        while self.accept_token_type(res, c.ID_SYM):
            arg_name_toks.append(self.previous_tok)

        self.expect_token_type(res, 'RBR', UnclosedScopeError)
        if res.error: return res

        # <~ follows optional brackets
        if self.accept_token_type(res, 'INJ'):

            # statements start on next line
            if self.current_tok.type == 'LCR':
                self.update(res)

                self.expect_newline(res)
                if res.error: return res

                body = res.register(self.statements())
                if res.error: return res

                # function definition must end with if
                self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)

                # return multi line function definition
                return res.success(FunctionDefinitionNode(var_name_tok,
                                                          arg_name_toks,
                                                          body,
                                                          False))

            # one-line functions auto-return, so ignore the return keyword if it was included
            # if self.current_tok.matches(Token(c.ID_KWD, 'return')):
            #     self.update(res)
            self.accept_keyword(res, 'return')

            body = res.register(self.expr())
            if res.error: return res

            return res.success(FunctionDefinitionNode(var_name_tok,
                                                      arg_name_toks,
                                                      body,
                                                      True))

        # fail if no injection operator
        return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                              self.current_tok.pos_end,
                                              f"Expected '<~'"))

    def interface_def(self):
        res = ParseResult()

        self.expect_token_type(res, c.ID_SYM)
        var_name_tok = self.previous_tok

        self.expect(res, 'INJ', '<~', message=f"Expected '<~'")
        if res.error: return res

        body = res.register(self.statement())
        if res.error: return res

        return res.success(InterfaceDefinitionNode(var_name_tok,
                                                   body,
                                                   True))

    def struct_def(self):
        res = ParseResult()

        if self.accept_token_type(res, c.ID_SYM):
            var_name_tok = self.previous_tok

            self.expect_token_type(res, 'LBR')
            if res.error: return res

        else:
            var_name_tok = None
            self.expect_token_type(res, 'LBR', UnopenedScopeError)
            if res.error: return res

        arg_name_toks = []
        while self.accept_token_type(res, c.ID_SYM):
            arg_name_toks.append(self.previous_tok)

        self.expect(res, 'RBR', ']', message=f"Expected identifier or ']'", err_type=UnclosedScopeError)
        if res.error: return res

        # { follows optional brackets
        if self.accept_token_type(res, 'LCR'):

            # statements start on next line
            if self.accept_newline(res):
                body = res.register(self.statements())
                if res.error: return res

                self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)
                if res.error: return res

                # return multi line function definition
                return res.success(StructDefinitionNode(var_name_tok,
                                                        arg_name_toks,
                                                        body,
                                                        True))

        # fail if no injection operator
        # TODO: why is this here?
        # UPDATE: when I comment this call out, I get:
        # FAILED tests/test_parser.py::TestParserErrors::test_invalid_struct_7 - AttributeError: 'NoneType' object has no attribute 'advance_count'
        # FAILED tests/test_parser.py::TestParserErrors::test_invalid_struct_8 - AttributeError: 'NoneType' object has no attribute 'advance_count'
        return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                              self.current_tok.pos_end,
                                              f"Expected newline"))

    # general binop handler
    # continues as long as it keeps seeing a token that it expects after
    # reading from func_a
    def bin_op(self, func_a, ops, func_b=None):

        if func_b is None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while any([op in ops for op in [self.current_tok.type,
                                        (self.current_tok.type, self.current_tok.value)]]):
            op_tok = self.current_tok
            self.update(res)
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

    def accept(self, res, token_type, token_val):
        if self.current_tok.type != token_type or self.current_tok.value != token_val:
            return False
        self.update(res)
        return True

    def accept_newline(self,  res):
        if self.current_tok.type != 'BREAK' or self.current_tok.value is not None:
            return False
        self.update(res)
        return True

    def accept_keyword(self, res, token_val):
        if self.current_tok.type != c.ID_KWD or self.current_tok.value != token_val:
            return False
        self.update(res)
        return True

    def accept_operator(self, res, token_val):
        if self.current_tok.type != c.ID_OPS or self.current_tok.value != token_val:
            return False
        self.update(res)
        return True

    def accept_token_type(self, res, token_type):
        if self.current_tok.type != token_type:
            return False
        self.update(res)
        return True

    def accept_one_token_type(self, res, token_types):
        if self.current_tok.type not in token_types:
            return False
        self.update(res)
        return True

    def accept_one(self, res, token_vals):
        if self.current_tok.value not in token_vals:
            return False
        self.update(res)
        return True

    def accept_optional(self, res, token_type, token_val):
        if self.current_tok.type != token_type or self.current_tok.value != token_val:
            return False
        self.update(res)
        return True

    def accept_one_optional(self, res, token_vals):
        if self.current_tok.value not in token_vals:
            return False
        self.update(res)
        return True

    def expect(self, res, token_type, token_val, message=None, err_type=InvalidSyntaxError):
        if not self.accept(res, token_type, token_val):
            message = f"Expected '{token_val}'" if message is None else message
            res.failure(err_type(self.current_tok.pos_start,
                                 self.current_tok.pos_end,
                                 message))

    def expect_newline(self, res):
        if not self.accept_newline(res):
            res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                           self.current_tok.pos_end,
                                           "Expected newline"))

    def expect_keyword(self, res, token_val, err_type=InvalidSyntaxError):
        if not self.accept_keyword(res, token_val):
            res.failure(err_type(self.current_tok.pos_start,
                                 self.current_tok.pos_end,
                                 f"Expected keyword '{token_val}'"))

    def expect_operator(self, res, token_val, err_type=InvalidSyntaxError):
        if not self.accept_operator(res, token_val):
            res.failure(err_type(self.current_tok.pos_start,
                                 self.current_tok.pos_end,
                                 f"Expected operator '{token_val}'"))

    def expect_token_type(self, res, token_type, err_type=InvalidSyntaxError):
        if not self.accept_token_type(res, token_type):
            res.failure(err_type(self.current_tok.pos_start,
                                 self.current_tok.pos_end,
                                 f"Expected token of type '{token_type}'"))

    def expect_one_token_type(self, res, token_types, err_type=InvalidSyntaxError):
        if not self.accept_one_token_type(res, token_types):
            res.failure(err_type(self.current_tok.pos_start,
                                 self.current_tok.pos_end,
                                 f"Expected type from: '{token_types}'"))

    def expect_one(self, res, token_vals, message=None, err_type=InvalidSyntaxError):
        if not self.accept_one(res, token_vals):
            message = f"Expected one of: {token_vals}" if message is None else message
            res.failure(err_type(self.current_tok.pos_start,
                                 self.current_tok.pos_end,
                                 message))

    def parse_block(self, res):
        self.expect(res, 'LCR', '{', err_type=UnopenedScopeError)
        if res.error:
            return None

        self.expect_newline(res)
        if res.error:
            return None

        body = res.register(self.statements())
        if res.error:
            return None

        self.expect(res, 'RCR', '}', err_type=UnclosedScopeError)
        if res.error:
            return None

        return body

    def parse_statement_or_block(self, res):
        if self.current_tok.type == 'LCR':
            body = self.parse_block(res)
            return body, True

        self.expect_operator(res, ':', err_type=UnopenedScopeError)
        if res.error:
            return None, None

        return res.register(self.statement()), False

    def consume_newlines(self, res):
        while self.current_tok.type == 'BREAK': self.update(res)
