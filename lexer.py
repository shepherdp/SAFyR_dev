from errors import *
from typedef import Position, Token
from result import LexResult

# lists for character sets
DGT = '1234567890'
LWR = 'abcdefghijklmnopqrstuvwxyz'
UPR = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
PNC = '+-*/=_?/\\|><.,;:\'"&^%$#@![]{}()~'
OPS = '+-*/=%^?!><&|~:.@;'
CON = '{}[]()'
WHT = '\n\t '

# all reserved keywords
KWDS = ['use', 'by', 'end', 'const', 'global', 'del',
        '?', '!?', '!', 'if', 'elif', 'else',
        'while', 'when', 'for', 'when', 'foreach', 'in',
        'return', 'continue', 'break', 'once',
        'int', 'flt', 'str', 'lst', 'map', 'var',
        'try', 'catch', 'defer']

# all multi-character operators
BIGRAPHS = ['+=', '-=', '*=', '/=', '^=', '%=',
            '++', '--', '==', '!=', '<=', '>=',
            '<~', '~>', '~&', '~|', '><', '!?',
            '</', '/>', '..', ':=', '::']

# all named operations
OPNAMES = {'+': 'PLS',
           '-': 'MNS',
           '*': 'MUL',
           '/': 'DIV',
           '%': 'MOD',
           '^': 'POW',
           '&': 'AND',
           '|': 'OR',
           '~': 'NOT',
           '[': 'LBR',
           ']': 'RBR',
           '(': 'LPR',
           ')': 'RPR',
           '{': 'LCR',
           '}': 'RCR',
           '@': 'AT',
           '.': 'DOT',
           '=': 'ASG',
           ':=': 'ASG',
           '+=': 'ASG',
           '-=': 'ASG',
           '*=': 'ASG',
           '/=': 'ASG',
           '%=': 'ASG',
           '^=': 'ASG',
           '<': 'LT',
           '>': 'GT',
           '<=': 'LE',
           '>=': 'GE',
           '!=': 'NE',
           '==': 'EQ',
           '<~': 'INJ',
           '~>': 'IN',
           '~&': 'NAND',
           '~|': 'NOR',
           '><': 'XOR',
           '..': 'RNG',
           '</': 'LSLC',
           '/>': 'RSLC'
           }


class Lexer:
    def __init__(self):

        self.state = 'new'
        self.pos = 0
        self.token = ''
        self.tokens = []
        self.input = ''
        self.t = {}
        self.name = ''

        self.linenum = 0
        self.colnum = 0
        self.linestart = 0
        self.currline = ''
        self.start_pos = Position(0, 0, 0, self.name, self.input)
        self.end_pos = self.start_pos.copy()

        self.load_rules()

    def load_rules(self):
        # state notes
        # new: ready to start a new token or skip whitespace
        # int: currently building integer token
        # flt: currently building float token
        # con: container token; ends after a single character
        # ops: operator token; can end after one or two characters
        # st1: currently building single-quoted string
        # st2: currently building double-quoted string
        # sym: currently building symbol (var name or keyword)
        # cmt: single line comment
        # cm2: multiline comment
        # fin: done building current token
        # xxx: fail
        states = ['new', 'int', 'flt', 'con', 'ops', 'dec',
                  'st1', 'st2', 'sym', 'fin', 'cmt', 'cm2',
                  'xxx']

        for s in states:
            self.t[s] = {}

        # initialize transitions for each state on seeing a digit
        for c in DGT:
            for s_ in ['new', 'int']:
                self.t[s_][c] = ['int', 1]
            for s_ in ['con', 'ops']:
                self.t[s_][c] = ['fin', 0]
            for s_ in ['flt', 'st1', 'st2', 'sym']:
                self.t[s_][c] = [s_, 1]
            self.t['dec'][c] = ['flt', 1]

        # initialize transitions for each state on seeing a letter
        for c in UPR + LWR:
            for s_ in ['con', 'ops', 'dec']:
                self.t[s_][c] = ['fin', 0]
            for s_ in ['int', 'flt']:
                self.t[s_][c] = ['xxx', 0]
            for s_ in ['new', 'sym']:
                self.t[s_][c] = ['sym', 1]
            for s_ in ['st1', 'st2']:
                self.t[s_][c] = [s_, 1]

        # initialize transitions for each state on seeing a punctuation mark
        for c in PNC:
            for s_ in ['new', 'int', 'flt', 'ops', 'sym']:
                self.t[s_][c] = ['xxx', 0]
            for s_ in ['st1', 'st2']:
                self.t[s_][c] = [s_, 1]
            self.t['con'][c] = ['fin', 0]
            self.t['dec'][c] = ['fin', 0]
            self.t['flt'][c] = ['fin', 0]

        # initialize transitions for each state on seeing an operator (overrides transitions from PNC)
        for c in OPS:
            for s_ in ['con', 'int', 'flt', 'sym']:
                self.t[s_][c] = ['fin', 0]
            for s_ in ['st1', 'st2']:
                self.t[s_][c] = [s_, 1]
            self.t['new'][c] = ['ops', 1]
            self.t['ops'][c] = ['fin', 1]
            self.t['dec']['.'] = ['fin', 1]
            self.t['flt']['.'] = ['fin', 0]

        # initialize transitions for each state on seeing a container symbol (overrides transitions from PNC)
        for c in CON:
            for s_ in ['con', 'int', 'flt', 'ops', 'sym']:
                self.t[s_][c] = ['fin', 0]
            for s_ in ['st1', 'st2']:
                self.t[s_][c] = [s_, 1]
            self.t['new'][c] = ['con', 1]

        # initialize transitions for each state on seeing whitespace
        for c in WHT:
            for s_ in ['new', 'st1', 'st2']:
                self.t[s_][c] = [s_, 1]
            for s_ in ['int', 'flt', 'ops', 'sym']:
                self.t[s_][c] = ['fin', 1]
            self.t['con'][c] = ['fin', 0]
            self.t['dec'][c] = ['fin', 1]

        # special transitions, e.g. closing off a string when the appropriate quote is encountered
        self.t['new']['.'] = ['dec', 1]
        self.t['int']['.'] = ['flt', 1]
        self.t['new']["'"] = ['st1', 1]
        self.t['new']['"'] = ['st2', 1]
        self.t['st1']["'"] = ['fin', 1]
        self.t['st2']['"'] = ['fin', 1]
        self.t['ops']['~'] = ['fin', 1]
        self.t['ops']['.'] = ['fin', 1]
        self.t['ops']['"'] = ['fin', 0]
        self.t['ops']["'"] = ['fin', 0]

        for s in ['int', 'flt', 'con', 'ops', 'dec', 'sym', 'fin', 'xxx', 'cmt']:
            self.t[s][';'] = ['fin', 0]
        for s in ['st1', 'st2']:
            self.t[s][';'] = [s, 1]
        self.t['new'][';'] = ['cmt', 1]
        for c in UPR + LWR + DGT + PNC + ' \t':
            self.t['cmt'][c] = ['cmt', 1]
        self.t['cmt']['\n'] = ['new', 1]
        self.t['cmt'][';'] = ['cm2', 1]

        for c in DGT + UPR + LWR + WHT + OPS + CON + PNC:
            self.t['cm2'][c] = ['cm2', 1]

    # move the read head by amt spaces
    def move(self, amt):
        self.pos += amt

    # set token back to empty and state to new after a token has been processed
    def reset_token(self):
        self.token = ''
        self.state = 'new'

    # execute a single processing step
    def transition(self):

        res = LexResult()

        # attach a copy of the current line of the program for use in error messages
        try:
            line = self.input[self.linestart:self.linestart + self.input[self.linestart:].index('\n')]
            self.currline = line
        except ValueError:
            self.currline = self.input[self.linestart:]

        # grab current character
        c = self.input[self.pos]

        # make a new start position if ready to build a new token
        if self.state == 'new': self.start_pos = Position(self.pos,
                                                          self.linenum,
                                                          self.colnum,
                                                          self.name,
                                                          self.currline)

        # unhandled character
        if c not in self.t[self.state]:
            self.end_pos = Position(self.pos,
                                    self.linenum,
                                    self.colnum+1,
                                    self.name,
                                    self.currline)
            return res.failure(IllegalInputCharacterError(self.start_pos,
                                                          self.end_pos,
                                                          f'Character [{c}] not supported.'))

        # get new state and number of steps to move
        s_, delta = self.t[self.state][c]

        # make sure that a string can directly follow an equals
        if self.token == '=' and c in "'\"":
            s_, delta = 'fin', 0

        # fail state
        if s_ == 'xxx':
            self.end_pos = Position(self.pos,
                                    self.linenum,
                                    self.colnum+1,
                                    self.name,
                                    self.currline)

            return res.failure(IllegalTokenFormatError(self.start_pos,
                                                       self.end_pos,
                                                       f'Encountered character [{c}] in state [{self.state}]'))

        # skip over current character
        elif s_ == 'new' and self.state == 'new':
            pass

        # single line comment
        elif s_ == 'cmt':
            self.state = s_

        # if in multiline comment, check to see if it is being closed
        elif s_ == 'cm2':
            if c == self.input[self.pos + 1] == ';':
                self.move(2)
                self.state = 'new'
            else: self.state = s_

        # finished with current token
        elif s_ == 'fin':
            # add current character to token if necessary
            self.end_pos = Position(self.pos,
                                    self.linenum,
                                    self.colnum,
                                    self.name,
                                    self.currline)

            # special cases for certain characters
            if self.token == c == '~':
                delta = 0
            if self.state == 'ops' and (self.token + c not in BIGRAPHS):
                delta = 0
            if c not in WHT:
                if delta:
                    self.token += c
                    self.end_pos.idx += 1
                    self.end_pos.col += 1

            # store current token and reset for next
            result = res.register(self.get_token())
            if res.error: return res
            self.tokens.append(result.value)
            self.reset_token()

        # add current character to token and change state
        else:
            self.token += c
            self.state = s_

        # track line and column numbers for error reporting
        if c == '\n':
            if self.state[:2] == 'st':
                return res.failure(UnmatchedQuoteError(self.start_pos,
                                                       self.end_pos,
                                                       'Unmatched quotation mark'))

            # modify current position and other data to prepare for next token
            self.end_pos = Position(self.pos, self.linenum, self.colnum, self.name, self.currline)
            self.linenum += 1
            self.colnum = 0
            self.currline = ''
            self.linestart = self.pos + 1
            self.token = ''
            self.tokens.append(Token('BREAK',
                                     None,
                                     pos_start=self.start_pos, pos_end=self.end_pos))

        else: self.colnum += delta

        # move the read head to prepare for the next step
        self.move(delta)

        return res.success(True)

    # take a raw text token and convert it to a Token object with the appropriate values
    def get_token(self):
        res = LexResult()
        s = self.token
        self.end_pos = Position(self.pos,
                                self.linenum,
                                self.colnum,
                                self.name,
                                self.currline)

        # numerical token
        if s[0] in DGT + '.':
            if '.' in s:
                if s == '.': return res.success(Token('DOT', s,
                                                      pos_start=self.start_pos, pos_end=self.end_pos))
                if s == '..': return res.success(Token('OPS', s,
                                                       pos_start=self.start_pos, pos_end=self.end_pos))

                return res.success(Token('FLT', float(s),
                                         pos_start=self.start_pos, pos_end=self.end_pos))
            else: return res.success(Token('INT', int(s),
                                           pos_start=self.start_pos, pos_end=self.end_pos))

        # symbol token
        if s[0] in UPR + LWR:
            if s in KWDS: return res.success(Token('KWD', s,
                                                   pos_start=self.start_pos, pos_end=self.end_pos))
            return res.success(Token('SYM', s,
                                     pos_start=self.start_pos, pos_end=self.end_pos))

        # string token
        if s[0] in '\'"':
            return res.success(Token('STR', s[1:-1],
                                     pos_start=self.start_pos,
                                     pos_end=self.end_pos))

        # operator or container token
        if s[0] in OPS + CON:
            if len(s) == 2 and s not in BIGRAPHS:
                return res.failure(IllegalTokenFormatError(self.start_pos,
                                                           self.end_pos,
                                                           f'Token [{s}] not supported.'))
            if s in KWDS:
                if s in KWDS: return res.success(Token('KWD', s,
                                                       pos_start=self.start_pos, pos_end=self.end_pos))

            if s in OPNAMES: return res.success(Token(OPNAMES[s], s,
                                                      pos_start=self.start_pos, pos_end=self.end_pos))

            return res.success(Token('OPS', s,
                                     pos_start=self.start_pos, pos_end=self.end_pos))

    def tokenize(self, text=None):
        res = LexResult()
        if text: self.input = text

        # process entire input string
        while self.pos < len(self.input):
            res.register(self.transition())
            if res.error: return res

        # if there is an active token when the end of the input is reached, store it
        if self.token:
            # handle unclosed quote in input
            if self.state in ['st1', 'st2']:
                self.end_pos = Position(self.pos,
                                        self.linenum,
                                        self.colnum+1,
                                        self.name,
                                        self.currline)

                return res.failure(UnmatchedQuoteError(self.start_pos,
                                                       self.end_pos,
                                                       'Unmatched quotation mark'))

            # add token to list
            result = res.register(self.get_token())
            if res.error: return res
            self.tokens.append(result.value)

        # attach EOF at the very end
        self.tokens.append(Token('EOF', None,
                                 Position(self.pos,
                                          self.linenum,
                                          self.colnum,
                                          self.name,
                                          self.currline)))

        return res.success(self.tokens)
