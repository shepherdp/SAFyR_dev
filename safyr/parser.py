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
        self.expect_keyword(res, 'use')
        if not res.error:

            # use must be followed by an identifier
            if self.current_tok.type == c.ID_SYM:
                fname = self.current_tok
                self.update(res)
            else: return res.failure(InvalidSyntaxError(pos_start,
                                                        self.current_tok.pos_end,
                                                        f'Expected file identifier'))

            # use must be followed by newline
            if self.current_tok.matches(Token('BREAK', None)): self.update(res)
            elif self.current_tok.matches(Token('EOF', None)): pass
            else: return res.failure(InvalidSyntaxError(pos_start,
                                                        self.current_tok.pos_end,
                                                        f'Expected newline'))

            return res.success(UseNode(fname))

        # return keyword handler
        res.error = None
        self.expect_keyword(res, 'return')
        if not res.error:
            expr, _ = res.try_register(self.expr())
            if not expr: self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr,
                                          pos_start,
                                          self.current_tok.pos_start.copy()))

        # del keyword handler
        res.error = None
        self.expect_keyword(res, 'del')
        if not res.error:

            # del must be followed by an identifier
            if not self.current_tok.type == c.ID_SYM:
                return res.failure(InvalidSyntaxError(pos_start,
                                                      self.current_tok.pos_end,
                                                      f'Expected identifier'))

            to_delete = self.current_tok
            self.update(res)

            return res.success(DeleteNode(to_delete))

        # continue keyword handler
        res.error = None
        self.expect_keyword(res, 'continue')
        if not res.error:
            return res.success(ContinueNode(pos_start,
                                            self.current_tok.pos_start.copy()))

        # once keyword handler
        res.error = None
        self.expect_keyword(res, 'once')
        if not res.error:
            return res.success(OnceNode(pos_start,
                                        self.current_tok.pos_start.copy()))

        # break keyword handler
        res.error = None
        self.expect_keyword(res, 'break')
        if not res.error:
            return res.success(BreakNode(pos_start,
                                         self.current_tok.pos_start.copy()))

        # try to read expression if no keyword statements found
        res.error = None
        expr = res.register(self.expr())
        if res.error: return res

        return res.success(expr)

    def expr(self):
        res = ParseResult()
        warn_msg = ''

        statictype = 'default'

        # check for constant declaration
        constvar = self.expect_optional(res, c.ID_KWD, 'const')

        # check for global declaration
        globalvar = self.expect_optional(res, c.ID_KWD, 'global')

        # warning about unnecessary var keyword
        if self.expect_optional(res, c.ID_KWD, 'var'):
            if not self.static:
                warn_msg = f'kwd <var> has no effect'
            statictype = 'var'

        # check for explicit type definition
        if self.current_tok.value in ['int', 'flt', 'str', 'lst', 'map']:
            statictype = self.current_tok.value
            self.update(res)

        # try to read a function definition
        if self.current_tok.matches(Token(c.ID_OPS, ':')):
            f = res.register(self.func_def())
            if res.error: return res
            return res.success(f)

        # try to read a struct definition
        if self.current_tok.matches(Token(c.ID_OPS, '::')):
            s = res.register(self.struct_def())
            if res.error: return res
            return res.success(s)

        # try to read an interface definition
        if self.current_tok.matches(Token('DOT', '.')):
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
        if self.current_tok.type == 'NOT':
            op_tok = self.current_tok
            self.update(res)

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
        if tok.type in ('PLS', 'MNS'):
            self.update(res)
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

        # register number
        if tok.type in (c.ID_INT, c.ID_FLT):
            self.update(res)
            return res.success(NumberNode(tok))

        # register string
        elif c.ID_STR in tok.type:
            self.update(res)
            return res.success(StringNode(tok))

        # register identifier
        elif tok.type == c.ID_SYM:
            self.update(res)
            return res.success(VarAccessNode(tok))

        # register parenthetical expression
        elif tok.type == 'LPR':
            self.update(res)
            expr = res.register(self.expr())
            if res.error: return res

            if self.current_tok.type == 'RPR':
                self.update(res)
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected ')'"))

        # register list
        elif tok.type == 'LBR':
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)

        # register map
        elif tok.type == 'LCR':
            map_expr = res.register(self.map_expr())
            if res.error: return res
            return res.success(map_expr)

        # register conditional chain
        elif tok.matches(Token(c.ID_KWD, '?')) or tok.matches(Token(c.ID_KWD, 'if')):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        # register for loop
        elif tok.matches(Token(c.ID_KWD, 'for')):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        # register iterator loop
        elif tok.matches(Token(c.ID_KWD, 'foreach')):
            foreach_expr = res.register(self.foreach_expr())
            if res.error: return res
            return res.success(foreach_expr)

        # register while loop
        elif tok.matches(Token(c.ID_KWD, 'while')):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        # register when trigger
        elif tok.matches(Token(c.ID_KWD, 'when')):
            when_expr = res.register(self.when_expr())
            if res.error: return res
            return res.success(when_expr)

        # register defer block
        elif tok.matches(Token(c.ID_KWD, 'defer')):
            defer_expr = res.register(self.defer_expr())
            if res.error: return res
            return res.success(defer_expr)

        # register try/catch block
        elif tok.matches(Token(c.ID_KWD, 'try')):
            try_expr = res.register(self.try_expr())
            if res.error: return res
            return res.success(try_expr)

        # register function definition
        elif tok.matches(Token(c.ID_OPS, ':')):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)

        # register struct definition
        elif tok.matches(Token(c.ID_OPS, '::')):
            struct_def = res.register(self.struct_def())
            if res.error: return res
            return res.success(struct_def)

        return res.failure(InvalidSyntaxError(tok.pos_start,
                                              tok.pos_end,
                                              "Expected atom"))

    def map_expr(self):
        res = ParseResult()
        elements = {}
        pos_start = self.current_tok.pos_start.copy()

        self.expect(res, 'LCR', '{', message="Expected '{'")
        if res.error: return res

        if self.current_tok.type == 'RCR':
            self.update(res)
        else:
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

        self.expect(res, 'LBR', '[', message="Expected '['")
        if res.error: return res

        if self.current_tok.type == 'RBR':
            self.update(res)
        else:
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

        self.expect_keyword(res, 'for')
        if res.error: return res

        if self.current_tok.type != c.ID_SYM:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected identifier"))
        var_name = self.current_tok
        self.update(res)

        self.expect(res, 'ASG', '=')
        if res.error: return res

        start_value = res.register(self.expr())
        if res.error: return res

        self.expect_operator(res, '..')
        if res.error: return res

        end_value = res.register(self.expr())
        if res.error: return res

        if self.current_tok.matches(Token(c.ID_OPS, '..')):
            self.update(res)
            step_value = res.register(self.expr())
            if res.error: return res
        else: step_value = None

        if self.current_tok.type == 'LCR':
            self.update(res)

            self.expect_newline(res)
            if res.error: return res

            body = res.register(self.statements())
            if res.error: return res

            self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)
            if res.error: return res

            return res.success(ForNode(var_name,
                                       start_value,
                                       end_value,
                                       step_value,
                                       body,
                                       True))

        self.expect_operator(res, ':', err_type=UnopenedScopeError)
        if res.error: return res

        body = res.register(self.statement())
        if res.error: return res

        return res.success(ForNode(var_name,
                                   start_value,
                                   end_value,
                                   step_value,
                                   body,
                                   False))

    def foreach_expr(self):
        res = ParseResult()

        self.expect_keyword(res, 'foreach')
        if res.error: return res

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

        if self.current_tok.type == 'LCR':
            self.update(res)

            self.expect_newline(res)
            if res.error: return res

            body = res.register(self.statements())
            if res.error: return res

            self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)
            if res.error: return res

            return res.success(ForEachNode(var_name, container, body, True))

        if not self.current_tok.matches(Token(c.ID_OPS, ':')):
            return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  "Expected ':' or '{'"))
        self.update(res)

        body = res.register(self.statement())
        if res.error: return res

        return res.success(ForEachNode(var_name,
                                       container,
                                       body,
                                       False))

    def while_expr(self):
        res = ParseResult()

        self.expect_keyword(res, 'while')
        if res.error: return res

        condition = res.register(self.expr())
        if res.error: return res

        self.expect(res, 'LCR', '{')
        if not res.error:

            self.expect_newline(res)
            if res.error: return res

            body = res.register(self.statements())
            if res.error: return res

            self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)
            if res.error: return res

            return res.success(WhileNode(condition,
                                         body,
                                         True))

        res.error = None
        self.expect_operator(res, ':', err_type=UnopenedScopeError)
        if res.error: return res

        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhileNode(condition,
                                     body,
                                     False))

    def when_expr(self):
        res = ParseResult()

        self.expect_keyword(res, 'when')
        if res.error: return res

        condition = res.register(self.expr())
        if res.error: return res

        self.expect(res, 'LCR', '{')
        if not res.error:

            self.expect_newline(res)
            if res.error: return res

            body = res.register(self.statements())
            if res.error: return res

            self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)
            if res.error: return res

            return res.success(WhenNode(condition,
                                        body,
                                        True))

        res.error = None
        self.expect_operator(res, ':', err_type=UnopenedScopeError)
        if res.error: return res
        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhenNode(condition,
                                    body,
                                    False))

    def defer_expr(self):
        res = ParseResult()

        self.expect_keyword(res, 'defer')
        if res.error: return res

        if self.current_tok.type == 'LCR':
            self.update(res)

            self.expect_newline(res)
            if res.error: return res

            body = res.register(self.statements())
            if res.error: return res

            self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)
            if res.error: return res

            return res.success(DeferNode(body,
                                         True))

        self.expect_operator(res, ':', err_type=UnopenedScopeError)
        if res.error: return res
        body = res.register(self.statement())
        if res.error: return res

        return res.success(DeferNode(body,
                                     False))

    def try_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(Token(c.ID_KWD, 'try')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected 'try'"))
        # self.expect_keyword(res, 'try')
        # if res.error: return res

        try_tok = self.current_tok
        self.update(res)

        if self.current_tok.type == 'LCR':
            self.update(res)

            self.expect_newline(res)
            if res.error: return res

            try_node = res.register(self.statements())
            if res.error: return res

            self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)
            if res.error: return res

        elif self.current_tok.matches(Token(c.ID_OPS, ':')):
            self.update(res)
            try_node = res.register(self.statement())
            if res.error: return res
        else: return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                    self.current_tok.pos_end,
                                                    "Expected ':' or '{'"))

        self.consume_newlines(res)

        self.expect_keyword(res, 'catch')
        if res.error: return res

        if self.current_tok.type == 'LCR':
            self.update(res)

            self.expect_newline(res)
            if res.error: return res

            catch_node = res.register(self.statements())
            if res.error: return res

            self.expect(res, 'RCR', '}', message="Expected '}'", err_type=UnclosedScopeError)
            if res.error: return res

        elif self.current_tok.matches(Token(c.ID_OPS, ':')):
            self.update(res)
            catch_node = res.register(self.statement())
            if res.error: return res

        else: return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                    self.current_tok.pos_end,
                                                    "Expected ':' or '{'"))

        return res.success(ErrorHandlerNode(try_tok, try_node, catch_node))

    def func_def(self):
        res = ParseResult()

        self.expect_operator(res, ':')
        if res.error: return res

        if self.current_tok.type == c.ID_SYM:
            var_name_tok = self.current_tok
            self.update(res)

            if self.current_tok.type != 'LBR':
                return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected '['"))
        else:
            var_name_tok = None
            if self.current_tok.type != 'LBR':
                return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected identifier or '['"))

        self.update(res)

        arg_name_toks = []
        if self.current_tok.type == c.ID_SYM:
            while self.current_tok.type == c.ID_SYM:
                arg_name_toks.append(self.current_tok)
                self.update(res)

            if self.current_tok.type != 'RBR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected ']'"))
        else:
            if self.current_tok.type != 'RBR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected identifier or ']'"))
        self.update(res)

        # <~ follows optional brackets
        if self.current_tok.type == 'INJ':
            self.update(res)

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
            if self.current_tok.matches(Token(c.ID_KWD, 'return')):
                self.update(res)

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

        self.expect(res, 'DOT', '.', message=f"Expected '.'")
        if res.error: return res

        if self.current_tok.type != c.ID_SYM:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected identifier"))
        var_name_tok = self.current_tok
        self.update(res)

        self.expect(res, 'INJ', '<~', message=f"Expected '<~'")
        if res.error: return res
        body = res.register(self.statement())
        if res.error: return res

        return res.success(InterfaceDefinitionNode(var_name_tok,
                                                   body,
                                                   True))

    def struct_def(self):
        res = ParseResult()

        self.expect_operator(res, '::')
        if res.error: return res

        if self.current_tok.type == c.ID_SYM:
            var_name_tok = self.current_tok
            self.update(res)

            if self.current_tok.type != 'LBR':
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected '['"))
        else:
            var_name_tok = None
            if self.current_tok.type != 'LBR':
                return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected identifier or '['"))
        self.update(res)

        arg_name_toks = []
        while self.current_tok.type == c.ID_SYM:
            arg_name_toks.append(self.current_tok)
            self.update(res)

        self.expect(res, 'RBR', ']', message=f"Expected identifier or ']'", err_type=UnclosedScopeError)
        if res.error: return res

        # { follows optional brackets
        if self.current_tok.type == 'LCR':
            self.update(res)

            # statements start on next line
            if self.current_tok.type == 'BREAK':
                self.update(res)
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

    def expect(self, res, token_type, token_val, message=None, err_type=InvalidSyntaxError):
        if self.current_tok.type != token_type or self.current_tok.value != token_val:
            if message is None:
                message = f"Expected {token_type}"

            res.failure(err_type(self.current_tok.pos_start,
                                 self.current_tok.pos_end,
                                 message))
            return
        self.update(res)

    def expect_newline(self, res):
        if self.current_tok.type != 'BREAK' or self.current_tok.value is not None:
            res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                           self.current_tok.pos_end,
                                           "Expected newline"))
            return
        self.update(res)

    def expect_keyword(self, res, token_val, err_type=InvalidSyntaxError):
        if self.current_tok.type != c.ID_KWD or self.current_tok.value != token_val:
            res.failure(err_type(self.current_tok.pos_start,
                                    self.current_tok.pos_end,
                                    f"Expected keyword '{token_val}'"))
            return
        self.update(res)

    def expect_operator(self, res, token_val, err_type=InvalidSyntaxError):
        if self.current_tok.type != c.ID_OPS or self.current_tok.value != token_val:
            res.failure(err_type(self.current_tok.pos_start,
                                 self.current_tok.pos_end,
                                 f"Expected operator '{token_val}'"))
            return
        self.update(res)

    def expect_one(self, res, token_vals, message=None, err_type=InvalidSyntaxError):
        if self.current_tok.value not in token_vals:
            if message is None:
                message = f"Expected one of: {token_vals}"

            res.failure(err_type(self.current_tok.pos_start,
                                    self.current_tok.pos_end,
                                    message))
            return
        self.update(res)

    def expect_optional(self, res, token_type, token_val):
        if self.current_tok.type != token_type or self.current_tok.value != token_val:
            return False
        self.update(res)
        return True

    def expect_one_optional(self, res, token_vals):
        if self.current_tok.value not in token_vals:
            return False
        self.update(res)
        return True

    def consume_newlines(self, res):
        while self.current_tok.type == 'BREAK':
            self.update(res)
