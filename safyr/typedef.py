from .errors import *
from .result import RuntimeResult
from .node import VarAssignNode
import os
from random import random


class Position:
    """Class for tracking positions of tokens in source files.
    
    Parameters:
    idx  :
    ln   :
    col  :
    fn   :
    ftxt :
    """
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self):
        self.idx += 1
        self.col += 1
        return self

    def __repr__(self):
        return f'idx: {self.idx} line: {self.ln} col: {self.col} name: {self.fn}'

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


class Token:
    """Class representing individual input tokens.
    
    Parameters
    ----------
    _type      :
    _value     :
    _pos_start :
    _pos_end   :
    """
    
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, other):
        """
        """
        return self == other

    def __repr__(self):
        """
        """
        if self.value is not None: return f'{self.type}:{self.value}'
        return f'{self.type}'

    def __eq__(self, other):
        """
        """
        return self.value == other.value and self.type == other.type

class SymbolTable:
    
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
        self.globals = []

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            if name in self.parent.globals:
                return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


class Context:
    
    def __init__(self, display_name, parent=None, parent_entry_pos=None, root='.'):
        self.display_name = display_name
        self.root = root
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None
