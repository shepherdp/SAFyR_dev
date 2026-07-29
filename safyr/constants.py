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