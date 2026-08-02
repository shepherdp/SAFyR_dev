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

        # skip newlines
        while self.current_tok.type == 'BREAK':
            self.update(res)

        # read in first statement
        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True
        e = None

        # read in any additional statements
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
        if self.current_tok.matches(Token(c.ID_KWD, 'use')):
            self.update(res)

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
        if self.current_tok.matches(Token(c.ID_KWD, 'return')):
            self.update(res)
            expr, _ = res.try_register(self.expr())
            if not expr: self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr,
                                          pos_start,
                                          self.current_tok.pos_start.copy()))

        # del keyword handler
        if self.current_tok.matches(Token(c.ID_KWD, 'del')):
            self.update(res)

            # del must be followed by an identifier
            if not self.current_tok.type == c.ID_SYM:
                return res.failure(InvalidSyntaxError(pos_start,
                                                      self.current_tok.pos_end,
                                                      f'Expected identifier'))

            to_delete = self.current_tok
            self.update(res)

            return res.success(DeleteNode(to_delete))

        # continue keyword handler
        if self.current_tok.matches(Token(c.ID_KWD, 'continue')):
            self.update(res)
            return res.success(ContinueNode(pos_start,
                                            self.current_tok.pos_start.copy()))

        # once keyword handler
        if self.current_tok.matches(Token(c.ID_KWD, 'once')):
            self.update(res)
            return res.success(OnceNode(pos_start,
                                            self.current_tok.pos_start.copy()))

        # break keyword handler
        if self.current_tok.matches(Token(c.ID_KWD, 'break')):
            self.update(res)
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
        constvar = False
        globalvar = False

        # check for constant declaration
        if self.current_tok.matches(Token(c.ID_KWD, 'const')):
            constvar = True
            self.update(res)

        # check for global declaration
        if self.current_tok.matches(Token(c.ID_KWD, 'global')):
            globalvar = True
            self.update(res)

        # warning about unnecessary var keyword
        if self.current_tok.matches(Token(c.ID_KWD, 'var')):
            if not self.static:
                warn_msg = f'kwd <var> has no effect'
            statictype = 'var'
            self.update(res)

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

        if self.current_tok.type != 'LCR':
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  "Expected '{'"))
        self.update(res)

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

                if not self.current_tok.matches(Token(c.ID_OPS, ':')):
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                          self.current_tok.pos_end,
                                                          f"Expected ':'"))
                self.update(res)

                value = res.register(self.expr())
                if res.error: return res

                elements[key] = value
                while self.current_tok.matches(Token('BREAK', None)):
                    self.update(res)

            if self.current_tok.type != 'RCR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected expression or ']'"))

            self.update(res)

        return res.success(MapNode(elements,
                                   pos_start,
                                   self.current_tok.pos_end.copy()))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != 'LBR':
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected '['"))
        self.update(res)

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

            if self.current_tok.type != 'RBR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected ']'"))
            self.update(res)

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

                if not self.current_tok.type == 'BREAK':
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                          self.current_tok.pos_end,
                                                          'Expected newline'))

                self.update(res)

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                if self.current_tok.type == 'RCR':
                    self.update(res)
                else:
                    return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                          self.current_tok.pos_end,
                                                          'Expected }'))

            else:
                if not self.current_tok.matches(Token(c.ID_OPS, ':')):
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                          self.current_tok.pos_end,
                                                          f"Expected ':'"))

                self.update(res)

                expr = res.register(self.expr())
                if res.error: return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        while self.current_tok.type == 'BREAK':
            self.update(res)

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

        if not self.current_tok.value in case_keywords:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected '{case_keywords}'"))

        self.update(res)

        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type == 'LCR':
            self.update(res)

            if not self.current_tok.type == 'BREAK':
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected newline"))

            self.update(res)

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
            if not self.current_tok.matches(Token(c.ID_OPS, ':')):
                return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected ':'"))
            self.update(res)

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

        if not self.current_tok.matches(Token(c.ID_KWD, 'for')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected 'for'"))
        self.update(res)

        if self.current_tok.type != c.ID_SYM:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected identifier"))
        var_name = self.current_tok
        self.update(res)

        if self.current_tok.value != '=':
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected '='"))
        self.update(res)

        start_value = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(Token(c.ID_OPS, '..')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected '..'"))
        self.update(res)

        end_value = res.register(self.expr())
        if res.error: return res

        if self.current_tok.matches(Token(c.ID_OPS, '..')):
            self.update(res)
            step_value = res.register(self.expr())
            if res.error: return res
        else: step_value = None

        if self.current_tok.type == 'LCR':
            self.update(res)

            if not self.current_tok.type == 'BREAK':
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected newline"))
            self.update(res)
            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.type == 'RCR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected '}'"))
            self.update(res)

            return res.success(ForNode(var_name,
                                       start_value,
                                       end_value,
                                       step_value,
                                       body,
                                       True))

        if not self.current_tok.matches(Token(c.ID_OPS, ':')):
            return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected ':'"))
        self.update(res)

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

        if not self.current_tok.matches(Token(c.ID_KWD, 'foreach')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected 'foreach'"))
        self.update(res)

        if self.current_tok.type != c.ID_SYM:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected identifier"))
        var_name = self.current_tok
        self.update(res)

        if not self.current_tok.matches(Token(c.ID_KWD, 'in')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected 'in'"))
        self.update(res)
        container = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type == 'LCR':
            self.update(res)
            if not self.current_tok.matches(Token('BREAK', None)):
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected newline"))
            self.update(res)

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.type == 'RCR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected '}'"))
            self.update(res)

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

        if not self.current_tok.matches(Token(c.ID_KWD, 'while')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected 'while'"))
        self.update(res)
        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type == 'LCR':
            self.update(res)

            if not self.current_tok.type == 'BREAK':
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected newline"))
            self.update(res)

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.type == 'RCR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected '}'"))
            self.update(res)

            return res.success(WhileNode(condition,
                                         body,
                                         True))

        if not self.current_tok.matches(Token(c.ID_OPS, ':')):
            return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  "Expected ':' or '{'"))
        self.update(res)
        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhileNode(condition,
                                     body,
                                     False))

    def when_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(Token(c.ID_KWD, 'when')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected 'when'"))
        self.update(res)
        condition = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type == 'LCR':
            self.update(res)

            if not self.current_tok.type == 'BREAK':
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected newline"))
            self.update(res)

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.type == 'RCR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected '}'"))
            self.update(res)

            return res.success(WhenNode(condition,
                                        body,
                                        True))

        if not self.current_tok.matches(Token(c.ID_OPS, ':')):
            return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  "Expected ':' or '{'"))
        self.update(res)
        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhenNode(condition,
                                    body,
                                    False))

    def defer_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(Token(c.ID_KWD, 'defer')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected 'defer'"))
        self.update(res)

        if self.current_tok.type == 'LCR':
            self.update(res)

            if not self.current_tok.type == 'BREAK':
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected newline"))
            self.update(res)

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.type == 'RCR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected '}'"))
            self.update(res)

            return res.success(DeferNode(body,
                                         True))

        if not self.current_tok.matches(Token(c.ID_OPS, ':')):
            return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  "Expected ':' or '{'"))
        self.update(res)
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
        try_tok = self.current_tok
        self.update(res)

        if self.current_tok.type == 'LCR':
            self.update(res)

            if not self.current_tok.matches(Token('BREAK', None)):
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected newline"))
            self.update(res)
            try_node = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.type == 'RCR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected '}'"))
            self.update(res)

        elif self.current_tok.matches(Token(c.ID_OPS, ':')):
            self.update(res)
            try_node = res.register(self.statement())
            if res.error: return res
        else: return res.failure(UnopenedScopeError(self.current_tok.pos_start,
                                                    self.current_tok.pos_end,
                                                    "Expected ':' or '{'"))

        while self.current_tok.type == 'BREAK':
            self.update(res)

        if not self.current_tok.matches(Token(c.ID_KWD, 'catch')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected 'catch'"))
        self.update(res)

        if self.current_tok.type == 'LCR':
            self.update(res)

            if not self.current_tok.matches(Token('BREAK', None)):
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected newline"))
            self.update(res)
            catch_node = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.type == 'RCR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      "Expected '}'"))
            self.update(res)

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

        if not self.current_tok.matches(Token(c.ID_OPS, ':')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected ':'"))
        self.update(res)

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

                if self.current_tok.type != 'BREAK':
                    return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                          self.current_tok.pos_end,
                                                          f"Expected newline"))
                self.update(res)
                body = res.register(self.statements())
                if res.error: return res

                # function definition must end with if
                if self.current_tok.type != 'RCR':
                    return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                          self.current_tok.pos_end,
                                                          "Expected '}'"))
                # advance past end
                self.update(res)

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

        if not self.current_tok.matches(Token('DOT', '.')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected '.'"))
        self.update(res)

        if self.current_tok.type != c.ID_SYM:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected identifier"))
        var_name_tok = self.current_tok
        self.update(res)

        if self.current_tok.type != 'INJ':
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected <~"))
        self.update(res)
        body = res.register(self.statement())
        if res.error: return res

        return res.success(InterfaceDefinitionNode(var_name_tok,
                                                   body,
                                                   True))

    def struct_def(self):
        res = ParseResult()

        if not self.current_tok.matches(Token(c.ID_OPS, '::')):
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected '::'"))
        self.update(res)

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
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected identifier or '['"))
        self.update(res)

        arg_name_toks = []
        while self.current_tok.type == c.ID_SYM:
            arg_name_toks.append(self.current_tok)
            self.update(res)

            if self.current_tok.type != 'RBR':
                return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                      self.current_tok.pos_end,
                                                      f"Expected ']'"))

        if self.current_tok.type != 'RBR':
            return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  f"Expected identifier or ']'"))
        self.update(res)

        # { follows optional brackets
        if self.current_tok.type == 'LCR':
            self.update(res)

            # statements start on next line
            if self.current_tok.type == 'BREAK':
                self.update(res)
                body = res.register(self.statements())
                if res.error: return res

                # function definition must end with if
                if not self.current_tok.type == 'RCR':
                    return res.failure(UnclosedScopeError(self.current_tok.pos_start,
                                                          self.current_tok.pos_end,
                                                          "Expected '}'"))
                # advance past end
                self.update(res)

                # return multi line function definition
                return res.success(StructDefinitionNode(var_name_tok,
                                                        arg_name_toks,
                                                        body,
                                                        True))

        # fail if no injection operator
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
